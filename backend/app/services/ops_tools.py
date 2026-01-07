import shlex
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import json
import re
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
from ..ssh_utils import SSHClient, ssh_manager
from ..log_reader import log_reader
from ..config import now_bj


def _now() -> datetime:
    """返回当前 UTC 时间。"""
    return now_bj()


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


async def _user_has_cluster_access(db: AsyncSession, user_name: str, cluster_id: int) -> bool:
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": user_name})
    uid_row = uid_res.first()
    if not uid_row:
        return False
    ok_res = await db.execute(
        text("SELECT 1 FROM user_cluster_mapping WHERE user_id=:uid AND cluster_id=:cid LIMIT 1"),
        {"uid": uid_row[0], "cid": cluster_id},
    )
    return ok_res.first() is not None


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
    if not getattr(n, "ssh_password", None):
        return {"error": "ssh_password_not_configured"}
    path_q = shlex.quote(path)
    cmd = f"tail -n {lines} {path_q}"
    if pattern:
        pat_q = shlex.quote(pattern)
        cmd = f"{cmd} | grep -E {pat_q}"
    start = _now()
    bash_cmd = f"bash -lc {shlex.quote(cmd)}"

    def _run():
        client = ssh_manager.get_connection(
            str(getattr(n, "hostname", node)),
            ip=str(getattr(n, "ip_address", "")),
            username=(ssh_user or getattr(n, "ssh_user", None) or "hadoop"),
            password=str(getattr(n, "ssh_password", "")),
        )
        return client.execute_command_with_timeout_and_status(bash_cmd, timeout=timeout)

    code, out, err = await asyncio.to_thread(_run)
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
    
    # 6. 更新集群状态 (改进：检查是否有失败日志)
    has_failed = any("failed" in log.lower() for log in logs)
    if not has_failed:
        cluster.health_status = "healthy"
    else:
        cluster.health_status = "error"
        
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


async def tool_read_cluster_log(
    db: AsyncSession,
    user_name: str,
    cluster_uuid: str,
    log_type: str,
    node_hostname: Optional[str] = None,
    lines: int = 100,
) -> Dict[str, Any]:
    """读取集群中特定服务类型的日志。"""
    import uuid as uuidlib
    try:
        uuidlib.UUID(cluster_uuid)
    except ValueError:
        return {"status": "error", "message": "invalid_uuid_format"}

    stmt = select(Cluster).where(Cluster.uuid == cluster_uuid)
    result = await db.execute(stmt)
    cluster = result.scalar_one_or_none()
    if not cluster:
        return {"status": "error", "message": "cluster_not_found"}
    if not await _user_has_cluster_access(db, user_name, int(cluster.id)):
        return {"status": "error", "message": "cluster_forbidden"}

    target_ip: Optional[str] = None
    target_hostname: Optional[str] = node_hostname
    ssh_user: Optional[str] = None
    ssh_password: Optional[str] = None

    if log_type.lower() == "namenode":
        target_ip = str(cluster.namenode_ip) if cluster.namenode_ip else None
        ssh_password = cluster.namenode_psw
        if not target_hostname:
            node_stmt = select(Node).where(Node.ip_address == cluster.namenode_ip)
            node_res = await db.execute(node_stmt)
            node_obj = node_res.scalar_one_or_none()
            target_hostname = node_obj.hostname if node_obj else "namenode"
            if node_obj and node_obj.ssh_user:
                ssh_user = node_obj.ssh_user
    elif log_type.lower() == "resourcemanager":
        target_ip = str(cluster.rm_ip) if cluster.rm_ip else None
        ssh_password = cluster.rm_psw
        if not target_hostname:
            node_stmt = select(Node).where(Node.ip_address == cluster.rm_ip)
            node_res = await db.execute(node_stmt)
            node_obj = node_res.scalar_one_or_none()
            target_hostname = node_obj.hostname if node_obj else "resourcemanager"
            if node_obj and node_obj.ssh_user:
                ssh_user = node_obj.ssh_user
    
    if not target_ip and target_hostname:
        node = await _find_accessible_node(db, user_name, target_hostname)
        if not node:
            return {"status": "error", "message": "node_not_found"}
        target_ip = str(node.ip_address)
        ssh_user = node.ssh_user or ssh_user
        ssh_password = node.ssh_password or ssh_password
    
    if not target_ip:
        return {"status": "error", "message": f"could_not_determine_node_for_{log_type}"}
    if not target_hostname:
        target_hostname = target_ip

    def _tail_via_ssh() -> Dict[str, Any]:
        ip = str(target_ip)
        hn = str(target_hostname)
        log_reader.find_working_log_dir(hn, ip)
        ssh_client = ssh_manager.get_connection(hn, ip=ip, username=ssh_user, password=ssh_password)
        paths = log_reader.get_log_file_paths(hn, log_type.lower())
        for p in paths:
            p_q = shlex.quote(p)
            out, err = ssh_client.execute_command(f"ls -la {p_q} 2>/dev/null")
            if err or not out.strip():
                continue
            out2, err2 = ssh_client.execute_command(f"tail -n {int(lines)} {p_q} 2>/dev/null")
            if err2:
                continue
            return {"status": "success", "node": hn, "log_type": log_type, "path": p, "content": out2}
        base_dir = log_reader._node_log_dir.get(hn, log_reader.log_dir)
        base_q = shlex.quote(base_dir)
        out, err = ssh_client.execute_command(f"ls -1 {base_q} 2>/dev/null")
        if err or not out.strip():
            return {"status": "error", "message": "log_dir_not_found", "node": hn}
        for fn in out.splitlines():
            f = (fn or "").strip()
            lf = f.lower()
            if not f:
                continue
            if log_type.lower() in lf and hn.lower() in lf and (lf.endswith(".log") or lf.endswith(".out") or lf.endswith(".out.1")):
                full = f"{base_dir}/{f}"
                full_q = shlex.quote(full)
                out2, err2 = ssh_client.execute_command(f"tail -n {int(lines)} {full_q} 2>/dev/null")
                if not err2:
                    return {"status": "success", "node": hn, "log_type": log_type, "path": full, "content": out2}
        return {"status": "error", "message": "log_file_not_found", "node": hn}

    return await asyncio.to_thread(_tail_via_ssh)


_FAULT_RULES: List[Dict[str, Any]] = [
    {
        "id": "hdfs_safemode",
        "severity": "high",
        "title": "NameNode 处于 SafeMode",
        "patterns": [r"SafeModeException", r"NameNode is in safe mode", r"Safe mode is ON"],
        "advice": "检查 DataNode 是否全部注册、磁盘与网络是否正常；必要时执行 hdfs dfsadmin -safemode leave。",
    },
    {
        "id": "hdfs_standby",
        "severity": "high",
        "title": "访问到 Standby NameNode",
        "patterns": [r"StandbyException", r"Operation category READ is not supported in state standby"],
        "advice": "确认客户端的 fs.defaultFS/HA 配置；确认 active/standby 切换状态是否正确。",
    },
    {
        "id": "rpc_connection_refused",
        "severity": "high",
        "title": "RPC 连接被拒绝或目标服务未启动",
        "patterns": [r"java\.net\.ConnectException:\s*Connection refused", r"Call to .* failed on local exception", r"Connection refused"],
        "advice": "确认对应守护进程是否存活、端口是否监听、iptables/安全组是否放通。",
    },
    {
        "id": "dns_or_route",
        "severity": "high",
        "title": "DNS/网络不可达",
        "patterns": [r"UnknownHostException", r"No route to host", r"Network is unreachable", r"Connection timed out"],
        "advice": "检查 DNS 解析、/etc/hosts、一致的主机名配置与网络连通性。",
    },
    {
        "id": "disk_no_space",
        "severity": "high",
        "title": "磁盘空间不足",
        "patterns": [r"No space left on device", r"DiskOutOfSpaceException", r"ENOSPC"],
        "advice": "清理磁盘、检查日志/临时目录增长；确认 DataNode 存储目录剩余空间。",
    },
    {
        "id": "permission_denied",
        "severity": "medium",
        "title": "权限不足或 HDFS ACL/权限问题",
        "patterns": [r"Permission denied", r"AccessControlException"],
        "advice": "检查用户/组映射、HDFS 权限与 ACL；确认相关目录权限与 umask。",
    },
    {
        "id": "kerberos_auth",
        "severity": "high",
        "title": "Kerberos 认证失败",
        "patterns": [r"GSSException", r"Failed to find any Kerberos tgt", r"Client cannot authenticate via:\s*\[TOKEN, KERBEROS\]"],
        "advice": "检查 KDC、keytab、principal、时间同步；确认客户端已 kinit 且票据未过期。",
    },
    {
        "id": "oom",
        "severity": "high",
        "title": "Java 内存溢出",
        "patterns": [r"OutOfMemoryError", r"Java heap space", r"GC overhead limit exceeded"],
        "advice": "检查相关服务 JVM 参数（-Xmx/-Xms）、容器/节点内存；结合 GC 日志定位内存泄漏或峰值。",
    },
    {
        "id": "jvm_exit_killed",
        "severity": "medium",
        "title": "进程异常退出或被杀",
        "patterns": [r"ExitCodeException exitCode=143", r"Killed by signal", r"Container killed"],
        "advice": "检查是否被资源管理器/系统 OOM killer 杀死；核对 YARN 队列资源与节点资源。",
    },
]


def _detect_faults_from_log_text(text: str, max_examples_per_rule: int = 3) -> List[Dict[str, Any]]:
    lines = (text or "").splitlines()
    hits: List[Dict[str, Any]] = []
    for rule in _FAULT_RULES:
        patterns = rule.get("patterns") or []
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        examples: List[Dict[str, Any]] = []
        for idx, line in enumerate(lines):
            if not line:
                continue
            if any(rgx.search(line) for rgx in compiled):
                examples.append({"lineNo": idx + 1, "line": line[:500]})
                if len(examples) >= max_examples_per_rule:
                    break
        if examples:
            hits.append(
                {
                    "id": rule.get("id"),
                    "severity": rule.get("severity"),
                    "title": rule.get("title"),
                    "advice": rule.get("advice"),
                    "examples": examples,
                    "matchCountApprox": len(examples),
                }
            )
    return hits


async def tool_detect_cluster_faults(
    db: AsyncSession,
    user_name: str,
    cluster_uuid: str,
    components: Optional[List[str]] = None,
    node_hostname: Optional[str] = None,
    lines: int = 200,
) -> Dict[str, Any]:
    import uuid as uuidlib

    try:
        uuidlib.UUID(cluster_uuid)
    except ValueError:
        return {"status": "error", "message": "invalid_uuid_format"}

    comps = components or ["namenode", "resourcemanager"]
    comps = [c for c in comps if isinstance(c, str) and c.strip()]
    comps = [c.strip().lower() for c in comps]
    if not comps:
        return {"status": "error", "message": "no_components"}

    reads: List[Dict[str, Any]] = []
    faults: List[Dict[str, Any]] = []

    for comp in comps:
        r = await tool_read_cluster_log(
            db=db,
            user_name=user_name,
            cluster_uuid=cluster_uuid,
            log_type=comp,
            node_hostname=node_hostname,
            lines=lines,
        )
        reads.append({k: r.get(k) for k in ("status", "node", "log_type", "path", "message")})
        if r.get("status") != "success":
            continue
        content = r.get("content") or ""
        comp_faults = _detect_faults_from_log_text(content)
        for f in comp_faults:
            f2 = dict(f)
            f2["component"] = comp
            f2["node"] = r.get("node")
            f2["path"] = r.get("path")
            faults.append(f2)

    severity_order = {"high": 0, "medium": 1, "low": 2}
    faults.sort(key=lambda x: (severity_order.get((x.get("severity") or "").lower(), 9), x.get("id") or ""))

    return {
        "status": "success",
        "cluster_uuid": cluster_uuid,
        "components": comps,
        "reads": reads,
        "faults": faults[:20],
    }


_OPS_COMMANDS: Dict[str, Dict[str, Any]] = {
    "jps": {"cmd": "jps -lm", "target": "all_nodes"},
    "hadoop_version": {"cmd": "hadoop version", "target": "namenode"},
    "hdfs_report": {"cmd": "hdfs dfsadmin -report", "target": "namenode"},
    "hdfs_safemode_get": {"cmd": "hdfs dfsadmin -safemode get", "target": "namenode"},
    "hdfs_ls_root": {"cmd": "hdfs dfs -ls / | head -n 200", "target": "namenode"},
    "yarn_node_list": {"cmd": "yarn node -list 2>/dev/null || yarn node -list -all", "target": "resourcemanager"},
    "yarn_application_list": {"cmd": "yarn application -list 2>/dev/null || yarn application -list -appStates RUNNING,ACCEPTED,SUBMITTED", "target": "resourcemanager"},
    "df_h": {"cmd": "df -h", "target": "all_nodes"},
    "free_h": {"cmd": "free -h", "target": "all_nodes"},
    "uptime": {"cmd": "uptime", "target": "all_nodes"},
}


async def tool_run_cluster_command(
    db: AsyncSession,
    user_name: str,
    cluster_uuid: str,
    command_key: str,
    target: Optional[str] = None,
    node_hostname: Optional[str] = None,
    timeout: int = 30,
    limit_nodes: int = 20,
) -> Dict[str, Any]:
    import uuid as uuidlib

    try:
        uuidlib.UUID(cluster_uuid)
    except ValueError:
        return {"status": "error", "message": "invalid_uuid_format"}

    spec = _OPS_COMMANDS.get((command_key or "").strip())
    if not spec:
        return {"status": "error", "message": "unsupported_command_key"}

    stmt = select(Cluster).where(Cluster.uuid == cluster_uuid)
    result = await db.execute(stmt)
    cluster = result.scalar_one_or_none()
    if not cluster:
        return {"status": "error", "message": "cluster_not_found"}
    if not await _user_has_cluster_access(db, user_name, int(cluster.id)):
        return {"status": "error", "message": "cluster_forbidden"}

    tgt = (target or spec.get("target") or "namenode").strip().lower()
    cmd = str(spec.get("cmd") or "").strip()
    if not cmd:
        return {"status": "error", "message": "empty_command"}

    bash_cmd = f"bash -lc {shlex.quote(cmd)}"

    async def _exec_on_node(hostname: str, ip: str, ssh_user: Optional[str], ssh_password: Optional[str]) -> Dict[str, Any]:
        def _run():
            client = ssh_manager.get_connection(hostname, ip=ip, username=ssh_user, password=ssh_password)
            exit_code, out, err = client.execute_command_with_timeout_and_status(bash_cmd, timeout=timeout)
            return exit_code, out, err

        exit_code, out, err = await asyncio.to_thread(_run)
        return {
            "node": hostname,
            "ip": ip,
            "exitCode": int(exit_code),
            "stdout": out,
            "stderr": err,
        }

    results: List[Dict[str, Any]] = []

    if tgt == "namenode":
        if not cluster.namenode_ip or not cluster.namenode_psw:
            return {"status": "error", "message": "namenode_not_configured"}
        ip = str(cluster.namenode_ip)
        node_stmt = select(Node).where(Node.ip_address == cluster.namenode_ip).limit(1)
        node_obj = (await db.execute(node_stmt)).scalars().first()
        hostname = node_obj.hostname if node_obj else "namenode"
        ssh_user = (node_obj.ssh_user if node_obj and node_obj.ssh_user else "hadoop")
        results.append(await _exec_on_node(hostname, ip, ssh_user, cluster.namenode_psw))

    elif tgt == "resourcemanager":
        if not cluster.rm_ip or not cluster.rm_psw:
            return {"status": "error", "message": "resourcemanager_not_configured"}
        ip = str(cluster.rm_ip)
        node_stmt = select(Node).where(Node.ip_address == cluster.rm_ip).limit(1)
        node_obj = (await db.execute(node_stmt)).scalars().first()
        hostname = node_obj.hostname if node_obj else "resourcemanager"
        ssh_user = (node_obj.ssh_user if node_obj and node_obj.ssh_user else "hadoop")
        results.append(await _exec_on_node(hostname, ip, ssh_user, cluster.rm_psw))

    elif tgt == "node":
        if not node_hostname:
            return {"status": "error", "message": "node_hostname_required"}
        node = await _find_accessible_node(db, user_name, node_hostname)
        if not node:
            return {"status": "error", "message": "node_not_found"}
        results.append(await _exec_on_node(node.hostname, str(node.ip_address), node.ssh_user or "hadoop", node.ssh_password))

    elif tgt == "all_nodes":
        nodes_stmt = select(Node).where(Node.cluster_id == cluster.id).limit(limit_nodes)
        nodes = (await db.execute(nodes_stmt)).scalars().all()
        for n in nodes:
            n2 = await _find_accessible_node(db, user_name, n.hostname)
            if not n2:
                continue
            results.append(await _exec_on_node(n2.hostname, str(n2.ip_address), n2.ssh_user or "hadoop", n2.ssh_password))

    else:
        return {"status": "error", "message": "invalid_target"}

    start = _now()
    exec_id = f"tool_{start.timestamp():.0f}"
    await _write_exec_log(db, exec_id, "run_cluster_command", "success", start, _now(), 0, user_name)

    return {
        "status": "success",
        "cluster_uuid": cluster_uuid,
        "command_key": command_key,
        "target": tgt,
        "executed": cmd,
        "results": results,
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
                "name": "read_cluster_log",
                "description": "读取集群中特定组件的日志（如 namenode, datanode, resourcemanager）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                        "log_type": {
                            "type": "string", 
                            "description": "组件类型，例如 namenode, datanode, resourcemanager, nodemanager, historyserver"
                        },
                        "node_hostname": {"type": "string", "description": "可选：指定节点的主机名。如果是 datanode 等非唯一组件，建议提供。"},
                        "lines": {"type": "integer", "default": 100, "description": "读取的行数"},
                    },
                    "required": ["cluster_uuid", "log_type"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "detect_cluster_faults",
                "description": "基于集群组件日志识别常见故障并输出结构化结果",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                        "components": {"type": "array", "items": {"type": "string"}, "description": "要分析的组件列表，例如 [namenode, resourcemanager, datanode]"},
                        "node_hostname": {"type": "string", "description": "可选：指定节点主机名（适用于 datanode 等多实例组件）"},
                        "lines": {"type": "integer", "default": 200, "description": "每个组件读取的行数"},
                    },
                    "required": ["cluster_uuid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_cluster_command",
                "description": "在集群节点上执行常用运维命令（白名单）并返回结果",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_uuid": {"type": "string", "description": "集群的 UUID"},
                        "command_key": {"type": "string", "description": "命令标识，例如 jps, hdfs_report, yarn_node_list, df_h"},
                        "target": {"type": "string", "description": "执行目标：namenode/resourcemanager/node/all_nodes；不传则按命令默认目标"},
                        "node_hostname": {"type": "string", "description": "target=node 时必填"},
                        "timeout": {"type": "integer", "default": 30},
                        "limit_nodes": {"type": "integer", "default": 20, "description": "target=all_nodes 时最多执行的节点数"},
                    },
                    "required": ["cluster_uuid", "command_key"],
                },
            },
        },
    ]
