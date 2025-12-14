import threading
import time
from typing import Dict, List, Optional
from app.log_reader import log_reader
from app.ssh_utils import ssh_manager
import os
import datetime

class LogCollector:
    """Real-time log collector for Hadoop cluster"""
    
    def __init__(self):
        self.collectors: Dict[str, threading.Thread] = {}
        self.is_running: bool = False
        self.collection_interval: int = 5  # 默认采集间隔，单位：秒
        self.log_dir: str = "./hadoop_logs_realtime"  # 默认日志保存目录
        
        # Create log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
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
                    
                    # Save new content to local file
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
                time.sleep(self.collection_interval * 2)
    
    def _save_log_chunk(self, node_name: str, log_type: str, content: str):
        """Save a chunk of log content to local file"""
        # Generate log file path
        log_file_path = os.path.join(
            self.log_dir,
            f"{node_name}_{log_type}.log"
        )
        
        # Append content to file
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(content)
    
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
        """Set the log directory"""
        self.log_dir = log_dir
        # Create directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        print(f"Set log directory to {self.log_dir}")

# Create a global log collector instance
log_collector = LogCollector()