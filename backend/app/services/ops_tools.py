import shlex
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import json
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..models.nodes import Node
from ..models.clusters import Cluster
from ..models.hadoop_exec_logs import HadoopExecLog
from ..ssh_utils import SSHClient
from .runner import run_remote_command


def _now() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


async def _find_accessible_node(db: AsyncSession, user_name: str, hostname: str) -> Optional[Node]:
    """校验用户对节点的访问权限，并返回节点对象。"""
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": user_name})
    uid_row = uid_res.first()
    if not uid_row:
        return None
    ids_res = await db.execute(text("SELECT cluster_id FROM user_cluster_mapping WHERE user_id=:uid"), {"uid": uid_row[0]})
    cluster_ids = [r[0] for r in ids_res.all()]
    if not cluster_ids:
        return None
    res = await db.execute(select(Node).where(Node.hostname == hostname, Node.cluster_id.in_(cluster_ids)).limit(1))
    return res.scalars().first()


async def _write_exec_log(db: AsyncSession, exec_id: str, command_type: str, status: str, start: datetime, end: Optional[datetime], exit_code: Optional[int], operator: str, stdout: Optional[str] = None, stderr: Optional[str] = None):
    """写入执行审计日志。"""
    # 查找 from_user_id 和 cluster_name
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": operator})
    uid_row = uid_res.first()
    from_user_id = uid_row[0] if uid_row else 1
    
    # 获取集群名称 (这里简化逻辑，取用户关联的第一个集群)
    cluster_res = await db.execute(text("""
        SELECT c.name 
        FROM clusters c 
        JOIN user_cluster_mapping m ON c.id = m.cluster_id 
        WHERE m.user_id = :uid LIMIT 1
    """), {"uid": from_user_id})
    cluster_row = cluster_res.first()
    cluster_name = cluster_row[0] if cluster_row else "default_cluster"

    row = HadoopExecLog(
        from_user_id=from_user_id,
        cluster_name=cluster_name,
        description=f"[{command_type}] {exec_id}",
        start_time=start,
        end_time=end
    )
    db.add(row)
    await db.flush()
    await db.commit()


async def tool_read_log(db: AsyncSession, user_name: str, node: str, path: str, lines: int = 200, pattern: Optional[str] = None, ssh_user: Optional[str] = None, timeout: int = 20) -> Dict[str, Any]:
    """工具：读取远端日志并可选筛选。"""
    n = await _find_accessible_node(db, user_name, node)
    if not n:
        return {"error": "node_not_found"}
    path_q = shlex.quote(path)
    cmd = f"tail -n {lines} {path_q}"
    if pattern:
        pat_q = shlex.quote(pattern)
        cmd = f"{cmd} | grep -E {pat_q}"
    start = _now()
    code, out, err = await run_remote_command(str(getattr(n, "ip_address", "")), ssh_user or "", cmd, timeout=timeout)
    end = _now()
    exec_id = f"tool_{start.timestamp():.0f}"
    await _write_exec_log(db, exec_id, "read_log", ("success" if code == 0 else "failed"), start, end, code, user_name, out, err)
    return {"execId": exec_id, "exitCode": code, "stdout": out, "stderr": err}


async def _fetch_page_text(client: httpx.AsyncClient, url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        # Skip if not a valid http url
        if not url.startswith("http"):
            return ""
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = await client.get(url, headers=headers, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Limit text length
            return text[:2000]
    except Exception:
        pass
    return ""


async def tool_web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """工具：联网搜索（Baidu）并读取网页内容。"""
    try:
        results = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        url = "https://www.baidu.com/s"
        params = {"wd": query}
        
        # Use sync requests for search page (stable)
        resp = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Baidu results are usually in div with class c-container
            for item in soup.select("div.c-container, div.result.c-container")[:max_results]:
                title_elem = item.select_one("h3")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                link_elem = item.select_one("a")
                href = link_elem.get("href") if link_elem else ""
                
                # Abstract/Snippet
                snippet = item.get_text(strip=True).replace(title, "")[:200]
                
                results.append({
                    "title": title,
                    "href": href,
                    "body": snippet,
                    "full_content": ""  # Placeholder
                })

        # Fetch full content for top 2 results
        if results:
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                tasks = []
                # Only fetch top 2 to avoid long wait
                for r in results[:2]:
                    tasks.append(_fetch_page_text(client, r["href"]))
                
                contents = await asyncio.gather(*tasks)
                
                for i, content in enumerate(contents):
                    if content:
                        results[i]["full_content"] = content
                        # Append note to body to indicate full content is available
                        results[i]["body"] += "\n[Full content fetched]"

        # Add current system time to help with "now" queries
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")
        return {"query": query, "current_time": current_time, "results": results}
    except Exception as e:
        return {"error": str(e)}


async def tool_start_cluster(db: AsyncSession, user_name: str, cluster_uuid: str) -> Dict[str, Any]:
    """工具：启动 Hadoop 集群。"""
    # 1. 权限与用户
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": user_name})
    uid_row = uid_res.first()
    user_id = uid_row[0] if uid_row else 1

    # 2. 查找集群
    res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
    cluster = res.scalars().first()
    if not cluster:
        return {"error": "cluster_not_found"}

    # 3. 获取 SSH 用户 (从关联节点中获取，默认为 hadoop)
    node_res = await db.execute(select(Node).where(Node.cluster_id == cluster.id).limit(1))
    node = node_res.scalars().first()
    ssh_user = node.ssh_user if node and node.ssh_user else "hadoop"

    start_time = _now()
    logs = []

    # 4. 在 NameNode 执行 start-dfs.sh
    if cluster.namenode_ip and cluster.namenode_psw:
        try:
            def run_nn_start():
                with SSHClient(str(cluster.namenode_ip), ssh_user, cluster.namenode_psw) as client:
                    return client.execute_command("start-dfs.sh")
            out, err = await asyncio.to_thread(run_nn_start)
            logs.append(f"NameNode ({cluster.namenode_ip}) start: {out} {err}")
        except Exception as e:
            logs.append(f"NameNode ({cluster.namenode_ip}) start failed: {str(e)}")
    
    # 5. 在 ResourceManager 执行 start-yarn.sh
    if cluster.rm_ip and cluster.rm_psw:
        try:
            def run_rm_start():
                with SSHClient(str(cluster.rm_ip), ssh_user, cluster.rm_psw) as client:
                    return client.execute_command("start-yarn.sh")
            out, err = await asyncio.to_thread(run_rm_start)
            logs.append(f"ResourceManager ({cluster.rm_ip}) start: {out} {err}")
        except Exception as e:
            logs.append(f"ResourceManager ({cluster.rm_ip}) start failed: {str(e)}")

    end_time = _now()
    
    # 6. 更新集群状态
    cluster.health_status = "healthy"
    cluster.updated_at = end_time
    await db.flush()

    # 7. 记录日志
    full_desc = " | ".join(logs)
    exec_row = HadoopExecLog(
        from_user_id=user_id,
        cluster_name=cluster.name,
        description=f"AI Tool Start Cluster: {full_desc}",
        start_time=start_time,
        end_time=end_time
    )
    db.add(exec_row)
    await db.commit()
    
    return {"status": "success", "logs": logs}


async def tool_stop_cluster(db: AsyncSession, user_name: str, cluster_uuid: str) -> Dict[str, Any]:
    """工具：停止 Hadoop 集群。"""
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": user_name})
    uid_row = uid_res.first()
    user_id = uid_row[0] if uid_row else 1

    res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
    cluster = res.scalars().first()
    if not cluster:
        return {"error": "cluster_not_found"}

    node_res = await db.execute(select(Node).where(Node.cluster_id == cluster.id).limit(1))
    node = node_res.scalars().first()
    ssh_user = node.ssh_user if node and node.ssh_user else "hadoop"

    start_time = _now()
    logs = []

    if cluster.namenode_ip and cluster.namenode_psw:
        try:
            def run_nn_stop():
                with SSHClient(str(cluster.namenode_ip), ssh_user, cluster.namenode_psw) as client:
                    return client.execute_command("stop-dfs.sh")
            out, err = await asyncio.to_thread(run_nn_stop)
            logs.append(f"NameNode ({cluster.namenode_ip}) stop: {out} {err}")
        except Exception as e:
            logs.append(f"NameNode ({cluster.namenode_ip}) stop failed: {str(e)}")
    
    if cluster.rm_ip and cluster.rm_psw:
        try:
            def run_rm_stop():
                with SSHClient(str(cluster.rm_ip), ssh_user, cluster.rm_psw) as client:
                    return client.execute_command("stop-yarn.sh")
            out, err = await asyncio.to_thread(run_rm_stop)
            logs.append(f"ResourceManager ({cluster.rm_ip}) stop: {out} {err}")
        except Exception as e:
            logs.append(f"ResourceManager ({cluster.rm_ip}) stop failed: {str(e)}")

    end_time = _now()
    
    cluster.health_status = "unknown"
    cluster.updated_at = end_time
    await db.flush()

    full_desc = " | ".join(logs)
    exec_row = HadoopExecLog(
        from_user_id=user_id,
        cluster_name=cluster.name,
        description=f"AI Tool Stop Cluster: {full_desc}",
        start_time=start_time,
        end_time=end_time
    )
    db.add(exec_row)
    await db.commit()
    
    return {"status": "success", "logs": logs}


async def tool_read_cluster_logs(db: AsyncSession, user_name: str, cluster_uuid: str, path: str, lines: int = 100) -> Dict[str, Any]:
    """工具：读取指定集群中所有节点的日志。"""
    # 1. 查找集群
    res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
    cluster = res.scalars().first()
    if not cluster:
        return {"error": "cluster_not_found"}

    # 2. 查找该集群下的所有节点
    node_res = await db.execute(select(Node).where(Node.cluster_id == cluster.id))
    nodes = node_res.scalars().all()
    if not nodes:
        return {"error": "no_nodes_found_in_cluster"}

    results = {}
    path_q = shlex.quote(path)
    cmd = f"tail -n {lines} {path_q}"

    # 3. 依次读取每个节点的日志
    for n in nodes:
        hostname = str(getattr(n, "hostname", "unknown"))
        ip = str(getattr(n, "ip_address", ""))
        ssh_user = str(getattr(n, "ssh_user", "hadoop"))
        ssh_pwd = str(getattr(n, "ssh_password", ""))

        if not ip or not ssh_pwd:
            results[hostname] = {"error": "missing_ssh_info"}
            continue

        try:
            def run_ssh():
                with SSHClient(ip, ssh_user, ssh_pwd) as client:
                    return client.execute_command(cmd)
            
            out, err = await asyncio.to_thread(run_ssh)
            results[hostname] = {
                "stdout": out,
                "stderr": err,
                "ip": ip
            }
        except Exception as e:
            results[hostname] = {"error": str(e)}

    return {
        "cluster_name": cluster.name,
        "path": path,
        "node_logs": results
    }


def openai_tools_schema() -> List[Dict[str, Any]]:
    """返回 OpenAI 兼容的工具定义（Function Calling）。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_log",
                "description": "读取指定节点的日志文件并可按正则筛选",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node": {"type": "string"},
                        "path": {"type": "string"},
                        "lines": {"type": "integer", "default": 200},
                        "pattern": {"type": "string"},
                        "sshUser": {"type": "string"},
                    },
                    "required": ["node", "path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "联网搜索互联网公开信息，当遇到未知错误码、技术名词或需要外部资料时使用",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "max_results": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "start_cluster",
                "description": "启动指定的 Hadoop 集群",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                    },
                    "required": ["cluster_uuid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "stop_cluster",
                "description": "停止指定的 Hadoop 集群",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                    },
                    "required": ["cluster_uuid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_cluster_logs",
                "description": "读取指定集群中所有节点的特定日志文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                        "path": {"type": "string", "description": "日志文件路径"},
                        "lines": {"type": "integer", "default": 100, "description": "每个节点读取的行数"},
                    },
                    "required": ["cluster_uuid", "path"],
                },
            },
        },
    ]