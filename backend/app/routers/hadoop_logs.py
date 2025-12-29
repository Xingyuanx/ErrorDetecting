from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..deps.auth import get_current_user
from ..log_reader import log_reader
from ..log_collector import log_collector
from ..ssh_utils import ssh_manager
from ..models.nodes import Node
from ..models.clusters import Cluster
from ..schemas import (
    LogRequest,
    LogResponse,
    MultiLogResponse,
    NodeListResponse,
    LogFilesResponse
)

router = APIRouter()

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
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name)
        
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
