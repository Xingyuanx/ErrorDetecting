import threading
import time
import uuid
import datetime
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .log_reader import log_reader
from .ssh_utils import ssh_manager
from .db import SessionLocal
from .models.hadoop_logs import HadoopLog
from sqlalchemy import text
import asyncio

class LogCollector:
    """Real-time log collector for Hadoop cluster"""
    
    def __init__(self):
        self.collectors: Dict[str, threading.Thread] = {}
        self.is_running: bool = False
        self.collection_interval: int = 5  # 默认采集间隔，单位：秒
        self._loops: Dict[str, asyncio.AbstractEventLoop] = {}
        self._targets: Dict[str, str] = {}
        self._line_counts: Dict[str, int] = {}
    
    def start_collection(self, node_name: str, log_type: str, ip: Optional[str] = None, interval: Optional[int] = None) -> bool:
        """Start real-time log collection for a specific node and log type"""
        if interval:
            self.collection_interval = interval
        
        collector_id = f"{node_name}_{log_type}"
        
        if collector_id in self.collectors and self.collectors[collector_id].is_alive():
            print(f"Collector {collector_id} is already running")
            return False
        
        # Start even if log file not yet exists; collector will self-check in loop
        
        # Create a new collector thread
        collector_thread = threading.Thread(
            target=self._collect_logs,
            args=(node_name, log_type, ip),
            name=collector_id,
            daemon=True
        )
        
        self.collectors[collector_id] = collector_thread
        collector_thread.start()
        print(f"Started collector {collector_id}")
        return True
    
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
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=datetime.timezone.utc)
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
                # 获取集群名称
                cluster_res = await session.execute(text("""
                    SELECT c.name 
                    FROM clusters c 
                    JOIN nodes n ON c.id = n.cluster_id 
                    WHERE n.hostname = :hn LIMIT 1
                """), {"hn": log_data["host"]})
                cluster_row = cluster_res.first()
                cluster_name = cluster_row[0] if cluster_row else "default_cluster"

                # Create HadoopLog instance
                hadoop_log = HadoopLog(
                    log_time=log_data["timestamp"],
                    node_host=log_data["host"],
                    title=log_data["service"],
                    info=log_data["message"],
                    cluster_name=cluster_name
                )
                
                # Add to session and commit
                session.add(hadoop_log)
                await session.commit()
        except Exception as e:
            print(f"Error saving log to database: {e}")
    
    async def _save_logs_to_db_batch(self, logs: List[Dict]):
        """Save a batch of logs to database in one transaction"""
        try:
            async with SessionLocal() as session:
                for log_data in logs:
                    cluster_res = await session.execute(text("""
                        SELECT c.name 
                        FROM clusters c 
                        JOIN nodes n ON c.id = n.cluster_id 
                        WHERE n.hostname = :hn LIMIT 1
                    """), {"hn": log_data["host"]})
                    cluster_row = cluster_res.first()
                    cluster_name = cluster_row[0] if cluster_row else "default_cluster"
                    hadoop_log = HadoopLog(
                        log_time=log_data["timestamp"],
                        node_host=log_data["host"],
                        title=log_data["service"],
                        info=log_data["message"],
                        cluster_name=cluster_name
                    )
                    session.add(hadoop_log)
                await session.commit()
        except Exception as e:
            print(f"Error batch saving logs: {e}")
    
    def _collect_logs(self, node_name: str, log_type: str, ip: str):
        """Internal method to collect logs continuously"""
        print(f"Starting log collection for {node_name}_{log_type}")
        
        collector_id = f"{node_name}_{log_type}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loops[collector_id] = loop

        last_file_size = 0
        last_line_count = self._line_counts.get(collector_id, 0)
        retry_count = 0
        max_retries = 3
        
        while collector_id in self.collectors:
            try:
                # Wait for next collection interval
                time.sleep(self.collection_interval)
                
                # Resolve target file once and reuse
                target = self._targets.get(collector_id)
                if not target:
                    try:
                        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
                        dirs = [
                            "/opt/module/hadoop-3.1.3/logs",
                            "/usr/local/hadoop/logs",
                            "/usr/local/hadoop-3.3.6/logs",
                            "/usr/local/hadoop-3.3.5/logs",
                            "/usr/local/hadoop-3.1.3/logs",
                            "/opt/hadoop/logs",
                            "/var/log/hadoop",
                        ]
                        for d in dirs:
                            out, err = ssh_client.execute_command(f"ls -1 {d} 2>/dev/null")
                            if not err and out.strip():
                                for fn in out.splitlines():
                                    f = fn.lower()
                                    if log_type in f and node_name in f:
                                        target = f"{d}/{fn}"
                                        break
                            if target:
                                break
                        if target:
                            self._targets[collector_id] = target
                    except Exception:
                        target = None
                if not target:
                    print(f"Log file {node_name}_{log_type} not found, will retry")
                    retry_count += 1
                    continue
                
                # Read current log content
                ssh_client = ssh_manager.get_connection(node_name, ip=ip)
                current_log_content = ""
                out2, err2 = ssh_client.execute_command(f"cat {target} 2>/dev/null")
                if not err2:
                    current_log_content = out2
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
                
                # Also track by line count to cover same-length encodings
                lines = current_log_content.splitlines()
                if len(lines) > last_line_count:
                    tail = "\n".join(lines[last_line_count:])
                    if tail.strip():
                        self._save_log_chunk(node_name, log_type, tail)
                        print(f"Collected {len(lines) - last_line_count} new lines (by count) from {node_name}_{log_type}")
                    last_line_count = len(lines)
                    self._line_counts[collector_id] = last_line_count
                
            except Exception as e:
                print(f"Error collecting logs from {node_name}_{log_type}: {e}")
                retry_count += 1
                
                if retry_count > max_retries:
                    print(f"Max retries reached for {node_name}_{log_type}, stopping collection")
                    self.stop_collection(node_name, log_type)
                    break
                
                print(f"Retrying in {self.collection_interval * 2} seconds... ({retry_count}/{max_retries})")
        
        try:
            loop = self._loops.pop(collector_id, None)
            if loop and loop.is_running():
                loop.stop()
            if loop:
                loop.close()
        except Exception:
            pass
    
    def _save_log_chunk(self, node_name: str, log_type: str, content: str):
        """Save a chunk of log content to database"""
        # Split content into lines
        lines = content.splitlines()
        
        # Parse each line and save to database
        log_batch: List[Dict] = []
        for line in lines:
            if line.strip():
                log_data = self._parse_log_line(line, node_name, log_type)
                log_batch.append(log_data)
        if not log_batch:
            return
        collector_id = f"{node_name}_{log_type}"
        loop = self._loops.get(collector_id)
        if loop:
            loop.run_until_complete(self._save_logs_to_db_batch(log_batch))
        else:
            asyncio.run(self._save_logs_to_db_batch(log_batch))
    
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
