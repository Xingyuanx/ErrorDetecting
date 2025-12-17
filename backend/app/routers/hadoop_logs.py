from fastapi import APIRouter, Depends, HTTPException, Query
from ..deps.auth import get_current_user
from ..log_reader import log_reader
from ..log_collector import log_collector
from ..ssh_utils import ssh_manager
from ..config import HADOOP_NODES
from ..schemas import (
    LogRequest,
    LogResponse,
    MultiLogResponse,
    NodeListResponse,
    LogFilesResponse
)

router = APIRouter()

@router.get("/hadoop/nodes/")
async def get_hadoop_nodes(user=Depends(get_current_user)):
    """Get list of all Hadoop nodes"""
    return NodeListResponse(nodes=list(HADOOP_NODES.keys()))

@router.get("/hadoop/logs/{node_name}/{log_type}/", response_model=LogResponse)
async def get_hadoop_log(node_name: str, log_type: str, user=Depends(get_current_user)):
    """Get log from a specific Hadoop node"""
    try:
        # Read log content
        log_content = log_reader.read_log(node_name, log_type)
        return LogResponse(
            node_name=node_name,
            log_type=log_type,
            log_content=log_content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hadoop/logs/all/{log_type}/", response_model=MultiLogResponse)
async def get_all_hadoop_nodes_log(log_type: str, user=Depends(get_current_user)):
    """Get logs from all Hadoop nodes"""
    try:
        # Read logs from all nodes
        logs = log_reader.read_all_nodes_log(log_type)
        return MultiLogResponse(logs=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hadoop/logs/files/{node_name}/", response_model=LogFilesResponse)
async def get_hadoop_log_files(node_name: str, user=Depends(get_current_user)):
    """Get list of log files on a specific Hadoop node"""
    try:
        # Get log files list
        log_files = log_reader.get_log_files_list(node_name)
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
async def start_hadoop_collector(node_name: str, log_type: str, interval: int = 5, user=Depends(get_current_user)):
    """Start log collection for a specific Hadoop node and log type"""
    try:
        log_collector.start_collection(node_name, log_type, interval)
        return {
            "message": f"Started log collection for {node_name}_{log_type}",
            "interval": interval
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hadoop/collectors/stop/{node_name}/{log_type}/")
async def stop_hadoop_collector(node_name: str, log_type: str, user=Depends(get_current_user)):
    """Stop log collection for a specific Hadoop node and log type"""
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
