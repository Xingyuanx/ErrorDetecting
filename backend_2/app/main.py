from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.log_reader import log_reader
from app.log_collector import log_collector
from app.ssh_utils import ssh_manager
from app.schemas import (
    LogRequest,
    SaveLogRequest,
    LogResponse,
    MultiLogResponse,
    SaveLogResponse,
    NodeListResponse,
    LogFilesResponse
)
from config import settings
from typing import Dict, Any

# Create FastAPI app instance
app = FastAPI(
    title="Hadoop Log Reader API",
    description="API for reading and managing Hadoop cluster logs remotely",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hadoop Log Reader API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/nodes/", response_model=NodeListResponse, tags=["Nodes"])
async def get_nodes():
    """Get list of all Hadoop nodes"""
    return NodeListResponse(nodes=list(settings.hadoop_nodes.keys()))

@app.get("/api/logs/{node_name}/{log_type}/", response_model=LogResponse, tags=["Logs"])
async def get_log(node_name: str, log_type: str):
    """Get log from a specific node"""
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

@app.get("/api/logs/all/{log_type}/", response_model=MultiLogResponse, tags=["Logs"])
async def get_all_nodes_log(log_type: str):
    """Get logs from all nodes"""
    try:
        # Read logs from all nodes
        logs = log_reader.read_all_nodes_log(log_type)
        return MultiLogResponse(logs=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/save/", response_model=SaveLogResponse, tags=["Logs"])
async def save_log(request: SaveLogRequest):
    """Save log from a specific node to local file"""
    try:
        # Save log to local file
        log_reader.save_log_to_local(
            request.node_name,
            request.log_type,
            request.local_file_path
        )
        return SaveLogResponse(
            message="Log saved successfully",
            local_file_path=request.local_file_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/save/all/{log_type}/", tags=["Logs"])
async def save_all_nodes_log(log_type: str, local_dir: str = "."):
    """Save logs from all nodes to local directory"""
    try:
        # Save logs from all nodes
        saved_files = log_reader.save_all_nodes_log(log_type, local_dir)
        return {
            "message": "Logs saved successfully",
            "saved_files": saved_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/files/{node_name}/", response_model=LogFilesResponse, tags=["Logs"])
def get_log_files(node_name: str):
    """Get list of log files on a specific node"""
    try:
        # Debug: Write to file instead of print
        with open("debug.log", "a") as f:
            f.write(f"\n=== Debug Log ===\n")
            f.write(f"Debug: Received node_name={node_name}\n")
            f.write(f"Debug: Nodes in settings: {list(settings.hadoop_nodes.keys())}\n")
        
        # Get log files list
        log_files = log_reader.get_log_files_list(node_name)
        return LogFilesResponse(
            node_name=node_name,
            log_files=log_files
        )
    except Exception as e:
        with open("debug.log", "a") as f:
            f.write(f"Debug: Exception occurred: {type(e).__name__}: {e}\n")
        raise HTTPException(status_code=500, detail=str(e))

# Add startup event to start log collection automatically
@app.on_event("startup")
async def startup_event():
    """Event handler for application startup"""
    print("=== Application Startup ===")
    print("Starting real-time log collection...")
    
    # Node service configuration based on cluster setup
    # Format: node_name: [service1, service2, ...]
    node_services = {
        "hadoop102": ["namenode", "datanode", "nodemanager"],
        "hadoop103": ["datanode", "resourcemanager", "nodemanager"],
        "hadoop104": ["datanode", "secondarynamenode", "nodemanager"],
        "hadoop105": ["datanode", "nodemanager"],
        "hadoop100": ["datanode", "nodemanager"]
    }
    
    # Start collecting logs based on actual services
    for node_name in node_services:
        for log_type in node_services[node_name]:
            try:
                log_collector.start_collection(node_name, log_type)
            except Exception as e:
                print(f"Error starting collector for {node_name}_{log_type}: {e}")

# Add API endpoints for log collection management
@app.get("/api/collectors/status/", tags=["Collectors"])
async def get_collectors_status():
    """Get status of all log collectors"""
    status = log_collector.get_collectors_status()
    return {
        "collectors": status,
        "total_running": sum(status.values())
    }

@app.post("/api/collectors/start/{node_name}/{log_type}/", tags=["Collectors"])
async def start_collector(node_name: str, log_type: str, interval: int = 5):
    """Start log collection for a specific node and log type"""
    try:
        log_collector.start_collection(node_name, log_type, interval)
        return {
            "message": f"Started log collection for {node_name}_{log_type}",
            "interval": interval
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collectors/stop/{node_name}/{log_type}/", tags=["Collectors"])
async def stop_collector(node_name: str, log_type: str):
    """Stop log collection for a specific node and log type"""
    try:
        log_collector.stop_collection(node_name, log_type)
        return {
            "message": f"Stopped log collection for {node_name}_{log_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collectors/stop/all/", tags=["Collectors"])
async def stop_all_collectors():
    """Stop all log collectors"""
    try:
        log_collector.stop_all_collections()
        return {
            "message": "Stopped all log collectors"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collectors/set-interval/{interval}/", tags=["Collectors"])
async def set_collection_interval(interval: int):
    """Set collection interval for all collectors"""
    try:
        log_collector.set_collection_interval(interval)
        return {
            "message": f"Set collection interval to {interval} seconds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collectors/set-log-dir/{log_dir}/", tags=["Collectors"])
async def set_log_directory(log_dir: str):
    """Set log directory for all collectors"""
    try:
        log_collector.set_log_dir(log_dir)
        return {
            "message": f"Set log directory to {log_dir}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nodes/{node_name}/execute/", tags=["Nodes"])
async def execute_command(node_name: str, command: str, timeout: int = 30):
    """Execute a command on a specific node"""
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

# Run the app if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)