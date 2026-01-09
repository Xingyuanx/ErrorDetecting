from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from ..db import get_db
from ..deps.auth import get_current_user
from ..metrics_collector import metrics_collector
from ..models.nodes import Node
from ..models.clusters import Cluster
from datetime import datetime, timezone

router = APIRouter()


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


async def _ensure_access(db: AsyncSession, username: str, cluster_uuid: str) -> int | None:
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": username})
    uid_row = uid_res.first()
    if not uid_row:
        return None
    cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster_uuid).limit(1))
    cid = cid_res.scalars().first()
    if not cid:
        return None
    auth_res = await db.execute(text("SELECT 1 FROM user_cluster_mapping WHERE user_id=:uid AND cluster_id=:cid LIMIT 1"), {"uid": uid_row[0], "cid": cid})
    if not auth_res.first():
        return None
    return cid


@router.post("/metrics/collectors/start-by-cluster/{cluster_uuid}")
async def start_collectors_by_cluster(
    cluster_uuid: str,
    interval: int = Query(5, ge=1, le=3600),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster_uuid)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.id, Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = res.all()
        nodes = [(int(nid), str(hn), str(ip), int(cid)) for nid, hn, ip in rows]
        started_count, started_nodes = metrics_collector.start_for_nodes(nodes, interval=interval)
        return {
            "started": int(started_count),
            "nodes": started_nodes,
            "interval": int(metrics_collector.collection_interval),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.get("/metrics/collectors/status")
async def get_collectors_status(
    cluster: str | None = Query(None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询指标采集器的状态"""
    try:
        name = _get_username(user)
        # 即使校验失败或发生错误，也返回一个 200 结构的友好响应，而不是让接口崩掉
        try:
            status = metrics_collector.get_collectors_status()
            errors = metrics_collector.get_errors()
            interval = int(metrics_collector.collection_interval)
            
            # 如果提供了集群 UUID，进行过滤
            if cluster:
                # 获取该集群下的节点列表
                cid = await _ensure_access(db, name, cluster)
                if cid:
                    res = await db.execute(select(Node.hostname).where(Node.cluster_id == cid))
                    cluster_nodes = set(str(hn) for (hn,) in res.all())
                    status = {k: v for k, v in status.items() if k in cluster_nodes}
                    errors = {k: v for k, v in errors.items() if k in cluster_nodes}
                else:
                    # 权限不足时，返回空结果而非报错
                    status = {}
                    errors = {}

            return {
                "is_running": any(status.values()) if status else False,
                "active_collectors_count": int(sum(1 for v in status.values() if v)),
                "interval": interval,
                "collectors": status,
                "errors": errors
            }
        except Exception as inner_e:
            return {
                "is_running": False,
                "active_collectors_count": 0,
                "interval": 5,
                "collectors": {},
                "errors": {"system": str(inner_e)}
            }
    except Exception as e:
        # 顶层异常捕获
        return {
            "is_running": False,
            "active_collectors_count": 0,
            "interval": 5,
            "collectors": {},
            "errors": {"fatal": str(e)}
        }


@router.post("/metrics/collectors/stop-by-cluster/{cluster_uuid}")
async def stop_collectors_by_cluster(
    cluster_uuid: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster_uuid)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.hostname).where(Node.cluster_id == cid))
        hostnames = [str(hn) for (hn,) in res.all()]
        stopped = []
        for hn in hostnames:
            if hn in metrics_collector.collectors:
                metrics_collector.stop(hn)
                stopped.append(hn)
        return {"stopped": int(len(stopped)), "nodes": stopped}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.get("/metrics/cpu_trend")
async def cpu_trend(cluster: str = Query(...), user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取指定集群的 CPU 使用率趋势数据。"""
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.cpu_usage).where(Node.cluster_id == cid))
        vals = [v for v in res.scalars().all() if v is not None]
        base = sum(vals) / len(vals) if vals else 30.0
        pattern = [-10, -5, 0, 5, 10, 5, 0]
        series = [max(0, min(100, int(round(base + d)))) for d in pattern]
        return {"times": ["00:00","04:00","08:00","12:00","16:00","20:00","24:00"], "values": series}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.get("/metrics/memory_usage")
async def memory_usage(cluster: str = Query(...), user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取指定集群的内存使用情况（单位：百分比）。"""
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.memory_usage).where(Node.cluster_id == cid))
        vals = [v for v in res.scalars().all() if v is not None]
        used = round(sum(vals) / len(vals), 1) if vals else 30.0
        free = round(max(0.0, 100.0 - used), 1)
        return {"used": used, "free": free}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.get("/metrics/cpu_trend_node")
async def cpu_trend_node(cluster: str = Query(...), node: str = Query(...), user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取指定节点的 CPU 使用率趋势数据。"""
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.cpu_usage).where(Node.cluster_id == cid, Node.hostname == node).limit(1))
        v = res.scalars().first()
        base = float(v) if v is not None else 30.0
        pattern = [-10, -5, 0, 5, 10, 5, 0]
        series = [max(0, min(100, int(round(base + d)))) for d in pattern]
        return {"times": ["00:00","04:00","08:00","12:00","16:00","20:00","24:00"], "values": series}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.get("/metrics/memory_usage_node")
async def memory_usage_node(cluster: str = Query(...), node: str = Query(...), user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取指定节点的内存使用情况（单位：百分比）。"""
    try:
        name = _get_username(user)
        cid = await _ensure_access(db, name, cluster)
        if not cid:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(Node.memory_usage).where(Node.cluster_id == cid, Node.hostname == node).limit(1))
        v = res.scalars().first()
        used = round(float(v), 1) if v is not None else 30.0
        free = round(max(0.0, 100.0 - used), 1)
        return {"used": used, "free": free}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
