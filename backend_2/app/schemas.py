from pydantic import BaseModel
from typing import List, Dict, Optional

class LogRequest(BaseModel):
    """Log request model"""
    node_name: str
    log_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SaveLogRequest(BaseModel):
    """Save log request model"""
    node_name: str
    log_type: str
    local_file_path: str

class LogResponse(BaseModel):
    """Log response model"""
    node_name: str
    log_type: str
    log_content: str

class MultiLogResponse(BaseModel):
    """Multiple logs response model"""
    logs: Dict[str, str]

class SaveLogResponse(BaseModel):
    """Save log response model"""
    message: str
    local_file_path: str

class NodeListResponse(BaseModel):
    """Node list response model"""
    nodes: List[str]

class LogFilesResponse(BaseModel):
    """Log files list response model"""
    node_name: str
    log_files: List[str]