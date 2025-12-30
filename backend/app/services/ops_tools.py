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
from ..models.hadoop_exec_logs import HadoopExecLog
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
        SELECT c.cluster_name 
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
    ]