import threading
import time
import uuid
import datetime
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .log_reader import log_reader
from .ssh_utils import ssh_manager
from .db import SessionLocal
from .models.system_logs import SystemLog

class LogCollector:
    """Real-time log collector for Hadoop cluster"""
    
    def __init__(self):
        self.collectors: Dict[str, threading.Thread] = {}
        self.is_running: bool = False
        self.collection_interval: int = 5  # 默认采集间隔，单位：秒
    
    def start_collection(self, node_name: str, log_type: str, interval: Optional[int] = None):
        """Start real-time log collection for a specific node and log type"""
        if interval:
            self.collection_interval = interval
        
        collector_id = f"{node_name}_{log_type}"
        
        if collector_id in self.collectors and self.collectors[collector_id].is_alive():
            print(f"Collector {collector_id} is already running")
            return
        
        # Check if log file exists first
        if not log_reader.check_log_file_exists(node_name, log_type):
            print(f"Log file {log_type} for node {node_name} does not exist, skipping collection")
            return
        
        # Create a new collector thread
        collector_thread = threading.Thread(
            target=self._collect_logs,
            args=(node_name, log_type),
            name=collector_id,
            daemon=True
        )
        
        self.collectors[collector_id] = collector_thread
        collector_thread.start()
        print(f"Started collector {collector_id}")
    
    def stop_collection(self, node_name: str, log_type: str):
        """Stop log collection for a specific node and log type"""
        collector_id = f"{node_name}_{log_type}"
        
        if collector_id in self.collectors:
            # Threads are daemon, so they will exit when main process exits
            # We just remove it from our tracking
            del self.collectors[collector_id]
            print(f"Stopped collector {collector_id}")
        else:
            print(f"Collector {collector_id} is not running")
    
    def stop_all_collections(self):
        """Stop all log collections"""
        for collector_id in list(self.collectors.keys()):
            self.stop_collection(*collector_id.split("_"))
    
    def _parse_log_line(self, line: str, node_name: str, log_type: str):
        """Parse a single log line and return a dictionary of log fields"""
        # Extract timestamp from the log line (format: [2023-12-17 10:00:00,123])
        timestamp = None
        log_level = "INFO"  # Default log level
        message = line
        exception = None
        
        # Simple log parsing logic
        if line.startswith('['):
            # Extract timestamp
            timestamp_end = line.find(']', 1)
            if timestamp_end > 0:
                timestamp_str = line[1:timestamp_end]
                try:
                    # Parse timestamp string to datetime object
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                except ValueError:
                    # If parsing fails, use current time
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        # Extract log level
        log_levels = ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        for level in log_levels:
            if f" {level} " in line:
                log_level = level
                break
        
        return {
            "timestamp": timestamp or datetime.datetime.now(datetime.timezone.utc),
            "log_level": log_level,
            "message": message,
            "host": node_name,
            "service": log_type,
            "raw_log": line
        }
    
    async def _save_log_to_db(self, log_data: Dict):
        """Save log data to database"""
        try:
            async with SessionLocal() as session:
                # Create SystemLog instance
                system_log = SystemLog(
                    log_id=str(uuid.uuid4()).replace('-', '')[:32],
                    timestamp=log_data["timestamp"],
                    host=log_data["host"],
                    service=log_data["service"],
                    log_level=log_data["log_level"],
                    message=log_data["message"],
                    raw_log=log_data["raw_log"],
                    processed=False,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )
                
                # Add to session and commit
                session.add(system_log)
                await session.commit()
        except Exception as e:
            print(f"Error saving log to database: {e}")
    
    def _collect_logs(self, node_name: str, log_type: str):
        """Internal method to collect logs continuously"""
        print(f"Starting log collection for {node_name}_{log_type}")
        
        last_file_size = 0
        retry_count = 0
        max_retries = 3
        
        while collector_id := f"{node_name}_{log_type}" in self.collectors:
            try:
                # Wait for next collection interval
                time.sleep(self.collection_interval)
                
                # Check if log file still exists
                if not log_reader.check_log_file_exists(node_name, log_type):
                    print(f"Log file {node_name}_{log_type} no longer exists, stopping collection")
                    self.stop_collection(node_name, log_type)
                    break
                
                # Read current log content
                current_log_content = log_reader.read_log(node_name, log_type)
                current_file_size = len(current_log_content)
                
                # Check if log file has new content
                if current_file_size > last_file_size:
                    # Extract new content
                    new_content = current_log_content[last_file_size:]
                    
                    # Save new content to database
                    self._save_log_chunk(node_name, log_type, new_content)
                    
                    # Update last file size
                    last_file_size = current_file_size
                    
                    print(f"Collected {len(new_content.splitlines())} new lines from {node_name}_{log_type}")
                    
                # Reset retry count on successful collection
                retry_count = 0
                
            except Exception as e:
                print(f"Error collecting logs from {node_name}_{log_type}: {e}")
                retry_count += 1
                
                if retry_count > max_retries:
                    print(f"Max retries reached for {node_name}_{log_type}, stopping collection")
                    self.stop_collection(node_name, log_type)
                    break
                
                print(f"Retrying in {self.collection_interval * 2} seconds... ({retry_count}/{max_retries})")
    
    def _save_log_chunk(self, node_name: str, log_type: str, content: str):
        """Save a chunk of log content to database"""
        import asyncio
        
        # Split content into lines
        lines = content.splitlines()
        
        # Parse each line and save to database
        for line in lines:
            if line.strip():
                # Parse log line
                log_data = self._parse_log_line(line, node_name, log_type)
                
                # Save to database asynchronously
                asyncio.run(self._save_log_to_db(log_data))
    
    def get_collectors_status(self) -> Dict[str, bool]:
        """Get the status of all collectors"""
        status = {}
        for collector_id, thread in self.collectors.items():
            status[collector_id] = thread.is_alive()
        return status
    
    def set_collection_interval(self, interval: int):
        """Set the collection interval"""
        self.collection_interval = max(1, interval)  # Ensure interval is at least 1 second
        print(f"Set collection interval to {self.collection_interval} seconds")
    
    def set_log_dir(self, log_dir: str):
        """Set the log directory (deprecated, logs are now stored in database)"""
        print(f"Warning: set_log_dir is deprecated. Logs are now stored in the database, not in local directory: {log_dir}")

# Create a global log collector instance
log_collector = LogCollector()