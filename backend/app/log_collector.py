import threading
import time
import uuid
import datetime
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from .log_reader import log_reader
from .ssh_utils import ssh_manager
from .db import SessionLocal
from .models.hadoop_logs import HadoopLog
from sqlalchemy import text
import asyncio
from .config import BJ_TZ, DATABASE_URL, APP_TIMEZONE

class LogCollector:
    """Real-time log collector for Hadoop cluster"""
    
    def __init__(self):
        self.collectors: Dict[str, threading.Thread] = {}
        self.is_running: bool = False
        self.collection_interval: int = 5  # 默认采集间隔，单位：秒
        self._loops: Dict[str, asyncio.AbstractEventLoop] = {}
        self._engines: Dict[str, AsyncEngine] = {}
        self._session_locals: Dict[str, async_sessionmaker[AsyncSession]] = {}
        self._intervals: Dict[str, int] = {}
        self._cluster_name_cache: Dict[str, str] = {}
        self._targets: Dict[str, str] = {}
        self._line_counts: Dict[str, int] = {}
        self.max_bytes_per_pull: int = 256 * 1024
    
    def start_collection(self, node_name: str, log_type: str, ip: Optional[str] = None, interval: Optional[int] = None) -> bool:
        """Start real-time log collection for a specific node and log type"""
        collector_id = f"{node_name}_{log_type}"
        if interval is not None:
            self._intervals[collector_id] = max(1, int(interval))
        
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
            self._intervals.pop(collector_id, None)
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
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=BJ_TZ)
                except ValueError:
                    # If parsing fails, use current time
                    timestamp = datetime.datetime.now(BJ_TZ)
        
        # Extract log level
        log_levels = ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        for level in log_levels:
            if f" {level} " in line:
                log_level = level
                break
        
        return {
            "timestamp": timestamp or datetime.datetime.now(BJ_TZ),
            "log_level": log_level,
            "message": message,
            "host": node_name,
            "service": log_type,
            "raw_log": line
        }
    
    async def _save_log_to_db(self, log_data: Dict, collector_id: str | None = None):
        """Save log data to database"""
        try:
            session_local = self._session_locals.get(collector_id) if collector_id else None
            async with (session_local() if session_local else SessionLocal()) as session:
                # 获取集群名称
                host = log_data["host"]
                cluster_name = self._cluster_name_cache.get(host)
                if not cluster_name:
                    cluster_res = await session.execute(text("""
                        SELECT c.name
                        FROM clusters c
                        JOIN nodes n ON c.id = n.cluster_id
                        WHERE n.hostname = :hn LIMIT 1
                    """), {"hn": host})
                    cluster_row = cluster_res.first()
                    cluster_name = cluster_row[0] if cluster_row else "default_cluster"
                    self._cluster_name_cache[host] = cluster_name

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
    
    async def _save_logs_to_db_batch(self, logs: List[Dict], collector_id: str | None = None):
        """Save a batch of logs to database in one transaction"""
        try:
            session_local = self._session_locals.get(collector_id) if collector_id else None
            async with (session_local() if session_local else SessionLocal()) as session:
                host = logs[0]["host"] if logs else None
                cluster_name = self._cluster_name_cache.get(host) if host else None
                if host and not cluster_name:
                    cluster_res = await session.execute(text("""
                        SELECT c.name
                        FROM clusters c
                        JOIN nodes n ON c.id = n.cluster_id
                        WHERE n.hostname = :hn LIMIT 1
                    """), {"hn": host})
                    cluster_row = cluster_res.first()
                    cluster_name = cluster_row[0] if cluster_row else "default_cluster"
                    self._cluster_name_cache[host] = cluster_name

                objs: list[HadoopLog] = []
                for log_data in logs:
                    objs.append(HadoopLog(
                        log_time=log_data["timestamp"],
                        node_host=log_data["host"],
                        title=log_data["service"],
                        info=log_data["message"],
                        cluster_name=cluster_name or "default_cluster",
                    ))
                session.add_all(objs)
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
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            connect_args={"server_settings": {"timezone": APP_TIMEZONE}},
            pool_size=1,
            max_overflow=0,
        )
        self._engines[collector_id] = engine
        self._session_locals[collector_id] = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        last_remote_size = 0
        retry_count = 0
        max_retries = 3
        
        while collector_id in self.collectors:
            try:
                # Wait for next collection interval
                interval = self._intervals.get(collector_id, self.collection_interval)
                time.sleep(interval)
                
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
                
                ssh_client = ssh_manager.get_connection(node_name, ip=ip)

                size_out, size_err = ssh_client.execute_command(f"stat -c %s {target} 2>/dev/null")
                if size_err:
                    retry_count += 1
                    continue
                try:
                    remote_size = int((size_out or "").strip())
                except Exception:
                    retry_count += 1
                    continue

                if remote_size < last_remote_size:
                    last_remote_size = 0

                if remote_size > last_remote_size:
                    delta = remote_size - last_remote_size
                    if delta > self.max_bytes_per_pull:
                        start_pos = remote_size - self.max_bytes_per_pull + 1
                        last_remote_size = remote_size - self.max_bytes_per_pull
                    else:
                        start_pos = last_remote_size + 1

                    out2, err2 = ssh_client.execute_command(f"tail -c +{start_pos} {target} 2>/dev/null")
                    if err2:
                        out2, err2 = ssh_client.execute_command(f"dd if={target} bs=1 skip={max(0, start_pos - 1)} 2>/dev/null")
                    if not err2 and out2 and out2.strip():
                        self._save_log_chunk(node_name, log_type, out2)
                        print(f"Collected new logs from {node_name}_{log_type} bytes={len(out2)}")

                    last_remote_size = remote_size

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
        
        try:
            loop = self._loops.pop(collector_id, None)
            engine = self._engines.pop(collector_id, None)
            self._session_locals.pop(collector_id, None)
            if engine and loop:
                loop.run_until_complete(engine.dispose())
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
            loop.run_until_complete(self._save_logs_to_db_batch(log_batch, collector_id=collector_id))
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
        for k in list(self._intervals.keys()):
            self._intervals[k] = self.collection_interval
        print(f"Set collection interval to {self.collection_interval} seconds")
    
    def set_log_dir(self, log_dir: str):
        """Set the log directory (deprecated, logs are now stored in database)"""
        print(f"Warning: set_log_dir is deprecated. Logs are now stored in the database, not in local directory: {log_dir}")

# Create a global log collector instance
log_collector = LogCollector()
