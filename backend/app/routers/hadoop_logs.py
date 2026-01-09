from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text
from ..db import get_db
from ..deps.auth import get_current_user
from ..log_reader import log_reader
from ..log_collector import log_collector
from ..ssh_utils import ssh_manager
from ..models.nodes import Node
from ..models.clusters import Cluster
from ..metrics_collector import metrics_collector
from ..models.hadoop_logs import HadoopLog
from datetime import datetime, timezone
import time
from ..models.node_metrics import NodeMetric
from ..models.cluster_metrics import ClusterMetric
from datetime import timedelta
from ..config import now_bj
from ..config import BJ_TZ
from zoneinfo import ZoneInfo
from ..schemas import (
    LogRequest,
    LogResponse,
    MultiLogResponse,
    NodeListResponse,
    LogFilesResponse
)

router = APIRouter()

async def _ensure_metrics_schema(db: AsyncSession):
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS node_metrics (
            id SERIAL PRIMARY KEY,
            cluster_id INTEGER,
            node_id INTEGER,
            hostname VARCHAR(100),
            cpu_usage DOUBLE PRECISION,
            memory_usage DOUBLE PRECISION,
            created_at TIMESTAMPTZ
        )
    """))
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS cluster_metrics (
            id SERIAL PRIMARY KEY,
            cluster_id INTEGER,
            cluster_name VARCHAR(100),
            cpu_avg DOUBLE PRECISION,
            memory_avg DOUBLE PRECISION,
            created_at TIMESTAMPTZ
        )
    """))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS node_id INTEGER"))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS hostname VARCHAR(100)"))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS cpu_usage DOUBLE PRECISION"))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS memory_usage DOUBLE PRECISION"))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ"))
    await db.execute(text("ALTER TABLE node_metrics ADD COLUMN IF NOT EXISTS cluster_id INTEGER"))
    await db.execute(text("ALTER TABLE cluster_metrics ADD COLUMN IF NOT EXISTS cluster_name VARCHAR(100)"))
    await db.execute(text("ALTER TABLE cluster_metrics ADD COLUMN IF NOT EXISTS cpu_avg DOUBLE PRECISION"))
    await db.execute(text("ALTER TABLE cluster_metrics ADD COLUMN IF NOT EXISTS memory_avg DOUBLE PRECISION"))
    await db.execute(text("ALTER TABLE cluster_metrics ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ"))
    await db.execute(text("ALTER TABLE cluster_metrics ADD COLUMN IF NOT EXISTS cluster_id INTEGER"))
    await db.commit()

def _parse_time(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=BJ_TZ)
        return dt.astimezone(BJ_TZ)
    except Exception:
        return None

@router.get("/logs")
async def list_logs(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cluster: str | None = Query(None),
    node: str | None = Query(None),
    source: str | None = Query(None),
    time_from: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    try:
        stmt = select(HadoopLog)
        count_stmt = select(func.count(HadoopLog.log_id))

        filters = []
        if cluster:
            filters.append(HadoopLog.cluster_name == cluster)
        if node:
            filters.append(HadoopLog.node_host == node)
        if source:
            like = f"%{source}%"
            filters.append(or_(HadoopLog.title.ilike(like), HadoopLog.info.ilike(like), HadoopLog.node_host.ilike(like)))
        tf = _parse_time(time_from)
        if tf:
            filters.append(HadoopLog.log_time >= tf)

        for f in filters:
            stmt = stmt.where(f)
            count_stmt = count_stmt.where(f)

        stmt = stmt.order_by(HadoopLog.log_time.desc()).offset((page - 1) * size).limit(size)
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        items = [
            {
                "id": r.log_id,
                "time": r.log_time.isoformat() if r.log_time else None,
                "cluster": r.cluster_name,
                "node": r.node_host,
                "title": r.title,
                "info": r.info,
            }
            for r in rows
        ]
        return {"items": items, "total": int(total)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing logs: {e}")
        raise HTTPException(status_code=500, detail="server_error")

async def get_node_ip(db: AsyncSession, node_name: str) -> str:
    result = await db.execute(select(Node.ip_address).where(Node.hostname == node_name))
    ip = result.scalar_one_or_none()
    if not ip:
        raise HTTPException(status_code=404, detail=f"Node {node_name} not found")
    return str(ip)

@router.get("/hadoop/nodes/")
async def get_hadoop_nodes(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get list of all Hadoop nodes"""
    # Assuming all nodes in DB are relevant, or filter by Cluster type if needed
    stmt = select(Node.hostname).join(Cluster)
    # Optional: .where(Cluster.type.ilike('%hadoop%'))
    result = await db.execute(stmt)
    nodes = result.scalars().all()
    return NodeListResponse(nodes=nodes)

@router.get("/hadoop/logs/{node_name}/{log_type}/", response_model=LogResponse)
async def get_hadoop_log(node_name: str, log_type: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get log from a specific Hadoop node"""
    ip = await get_node_ip(db, node_name)
    try:
        # Read log content
        log_content = log_reader.read_log(node_name, log_type, ip=ip)
        return LogResponse(
            node_name=node_name,
            log_type=log_type,
            log_content=log_content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hadoop/logs/all/{log_type}/", response_model=MultiLogResponse)
async def get_all_hadoop_nodes_log(log_type: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get logs from all Hadoop nodes"""
    stmt = select(Node.hostname, Node.ip_address).join(Cluster)
    result = await db.execute(stmt)
    nodes_data = result.all()
    
    nodes_list = [{"name": n[0], "ip": str(n[1])} for n in nodes_data]
    
    try:
        # Read logs from all nodes
        logs = log_reader.read_all_nodes_log(nodes_list, log_type)
        return MultiLogResponse(logs=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hadoop/logs/files/{node_name}/", response_model=LogFilesResponse)
async def get_hadoop_log_files(node_name: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get list of log files on a specific Hadoop node"""
    ip = await get_node_ip(db, node_name)
    try:
        # Get log files list
        log_files = log_reader.get_log_files_list(node_name, ip=ip)
        return LogFilesResponse(
            node_name=node_name,
            log_files=log_files
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Log collection management endpoints
@router.get("/hadoop/collectors/status/")
async def get_hadoop_collectors_status(user=Depends(get_current_user)):
    """Get status of all Hadoop log collectors"""
    status = log_collector.get_collectors_status()
    return {
        "collectors": status,
        "total_running": sum(status.values())
    }

@router.post("/hadoop/collectors/start/{node_name}/{log_type}/")
async def start_hadoop_collector(node_name: str, log_type: str, interval: int = 5, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start log collection for a specific Hadoop node and log type"""
    ip = await get_node_ip(db, node_name)
    try:
        log_collector.start_collection(node_name, log_type, ip=ip, interval=interval)
        return {
            "message": f"Started log collection for {node_name}_{log_type}",
            "interval": interval
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/stop/{node_name}/{log_type}/")
async def stop_hadoop_collector(node_name: str, log_type: str, user=Depends(get_current_user)):
    """Stop log collection for a specific Hadoop node and log type"""
    # stop doesn't need IP as it just stops the thread by ID
    try:
        log_collector.stop_collection(node_name, log_type)
        return {
            "message": f"Stopped log collection for {node_name}_{log_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/stop/all/")
async def stop_all_hadoop_collectors(user=Depends(get_current_user)):
    """Stop all Hadoop log collectors"""
    try:
        log_collector.stop_all_collections()
        return {
            "message": "Stopped all log collectors"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/set-interval/{interval}/")
async def set_hadoop_collection_interval(interval: int, user=Depends(get_current_user)):
    """Set collection interval for all Hadoop collectors"""
    try:
        log_collector.set_collection_interval(interval)
        return {
            "message": f"Set collection interval to {interval} seconds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/set-log-dir/{log_dir}/")
async def set_hadoop_log_directory(log_dir: str, user=Depends(get_current_user)):
    """Set log directory for all Hadoop collectors"""
    try:
        log_collector.set_log_dir(log_dir)
        return {
            "message": f"Set log directory to {log_dir}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/nodes/{node_name}/execute/")
async def execute_hadoop_command(node_name: str, command: str, timeout: int = 30, user=Depends(get_current_user)):
    """Execute a command on a specific Hadoop node"""
    try:
        from sqlalchemy import select
        from ..db import SessionLocal
        from ..models.nodes import Node
        async with SessionLocal() as db:
            res = await db.execute(select(Node.ip_address).where(Node.hostname == node_name).limit(1))
            ip = res.scalar_one_or_none()
        if not ip:
            raise HTTPException(status_code=404, detail=f"Node {node_name} not found")
        ssh_client = ssh_manager.get_connection(node_name, ip=str(ip))
        
        # Execute command with timeout
        stdout, stderr = ssh_client.execute_command_with_timeout(command, timeout)
        
        return {
            "node_name": node_name,
            "command": command,
            "stdout": stdout,
            "stderr": stderr,
            "status": "success" if not stderr else "error"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/start-by-cluster/{cluster_uuid}/")
async def start_collectors_by_cluster(cluster_uuid: str, interval: int = 5, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start log collection for all nodes of the cluster (by UUID), only for existing services"""
    try:
        cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster_uuid).limit(1))
        cid = cid_res.scalar_one_or_none()
        if cid is None:
            raise HTTPException(status_code=404, detail="cluster_not_found")
        nodes_res = await db.execute(select(Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = nodes_res.all()
        if not rows:
            return {"started": 0, "nodes": []}
        started = []
        for hn, ip in rows:
            ip_s = str(ip)
            files = []
            try:
                log_reader.find_working_log_dir(hn, ip_s)
                files = log_reader.get_log_files_list(hn, ip=ip_s)
            except Exception:
                files = []
            services = []
            for fn in files:
                f = fn.lower()
                if "namenode" in f:
                    services.append("namenode")
                elif "secondarynamenode" in f:
                    services.append("secondarynamenode")
                elif "datanode" in f:
                    services.append("datanode")
                elif "resourcemanager" in f:
                    services.append("resourcemanager")
                elif "nodemanager" in f:
                    services.append("nodemanager")
                elif "historyserver" in f:
                    services.append("historyserver")
            services = list(set(services))
            for t in services:
                ok = False
                try:
                    ok = log_collector.start_collection(hn, t, ip=ip_s, interval=interval)
                except Exception:
                    ok = False
                if ok:
                    started.append(f"{hn}_{t}")
        return {"started": len(started), "nodes": started, "interval": interval}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/backfill-by-cluster/{cluster_uuid}/")
async def backfill_logs_by_cluster(cluster_uuid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster_uuid).limit(1))
        cid = cid_res.scalar_one_or_none()
        if cid is None:
            raise HTTPException(status_code=404, detail="cluster_not_found")
        nodes_res = await db.execute(select(Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = nodes_res.all()
        if not rows:
            return {"backfilled": 0, "details": []}
        details = []
        for hn, ip in rows:
            ip_s = str(ip)
            ssh_client = ssh_manager.get_connection(hn, ip=ip_s)
            candidates = [
                "/opt/module/hadoop-3.1.3/logs",
                "/usr/local/hadoop/logs",
                "/usr/local/hadoop-3.3.6/logs",
                "/usr/local/hadoop-3.3.5/logs",
                "/usr/local/hadoop-3.1.3/logs",
                "/opt/hadoop/logs",
                "/var/log/hadoop",
            ]
            base = None
            for d in candidates:
                out, err = ssh_client.execute_command(f"ls -1 {d} 2>/dev/null")
                if not err and out.strip():
                    base = d
                    break
            services = []
            count = 0
            if base:
                out, err = ssh_client.execute_command(f"ls -1 {base} 2>/dev/null")
                if not err and out.strip():
                    for fn in out.splitlines():
                        f = fn.lower()
                        t = None
                        if "namenode" in f:
                            t = "namenode"
                        elif "secondarynamenode" in f:
                            t = "secondarynamenode"
                        elif "datanode" in f:
                            t = "datanode"
                        elif "resourcemanager" in f:
                            t = "resourcemanager"
                        elif "nodemanager" in f:
                            t = "nodemanager"
                        elif "historyserver" in f:
                            t = "historyserver"
                        if t:
                            services.append(t)
                            out2, err2 = ssh_client.execute_command(f"cat {base}/{fn} 2>/dev/null")
                            if not err2 and out2:
                                log_collector._save_log_chunk(hn, t, out2)
                                count += out2.count("\n")
            details.append({"node": hn, "services": list(set(services)), "lines": count})
        total_lines = sum(d["lines"] for d in details)
        return {"backfilled": total_lines, "details": details}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/{cluster_uuid}/")
async def sync_metrics(cluster_uuid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import select
        try:
            metrics_collector.stop_all()
        except Exception:
            pass
        cid_res = await db.execute(select(Cluster.id, Cluster.name).where(Cluster.uuid == cluster_uuid).limit(1))
        row = cid_res.first()
        if not row:
            raise HTTPException(status_code=404, detail="cluster_not_found")
        cid, cname = row
        nodes_res = await db.execute(select(Node.id, Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = nodes_res.all()
        now = now_bj()
        details = []
        for nid, hn, ip in rows:
            ssh_client = ssh_manager.get_connection(hn, ip=str(ip))
            out1, err1 = ssh_client.execute_command("cat /proc/stat | head -n 1")
            time.sleep(0.5)
            out2, err2 = ssh_client.execute_command("cat /proc/stat | head -n 1")
            cpu_pct = 0.0
            if not err1 and not err2 and out1.strip() and out2.strip():
                p1 = out1.strip().split()
                p2 = out2.strip().split()
                v1 = [int(x) for x in p1[1:]]
                v2 = [int(x) for x in p2[1:]]
                get1 = lambda i: (v1[i] if i < len(v1) else 0)
                get2 = lambda i: (v2[i] if i < len(v2) else 0)
                idle = (get2(3) + get2(4)) - (get1(3) + get1(4))
                total = (get2(0) - get1(0)) + (get2(1) - get1(1)) + (get2(2) - get1(2)) + idle + (get2(5) - get1(5)) + (get2(6) - get1(6)) + (get2(7) - get1(7))
                if total > 0:
                    cpu_pct = round((1.0 - idle / total) * 100.0, 2)
            outm, errm = ssh_client.execute_command("cat /proc/meminfo")
            mem_pct = 0.0
            if not errm and outm.strip():
                mt = 0
                ma = 0
                for line in outm.splitlines():
                    if line.startswith("MemTotal:"):
                        mt = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        ma = int(line.split()[1])
                if mt > 0:
                    mem_pct = round((1.0 - (ma / mt)) * 100.0, 2)
            details.append({"node": hn, "cpu": cpu_pct, "memory": mem_pct})
        if details:
            ca = round(sum(d["cpu"] for d in details) / len(details), 3)
            ma = round(sum(d["memory"] for d in details) / len(details), 3)
        else:
            ca = 0.0
            ma = 0.0
        return {"cluster": {"cpu_avg": round(ca, 2), "memory_avg": round(ma, 2), "time": now.isoformat(), "cluster_name": cname}, "nodes": details}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
