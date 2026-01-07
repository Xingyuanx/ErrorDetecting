import threading
import time
import datetime
import time as _time
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .ssh_utils import ssh_manager
from .db import SessionLocal
from .models.nodes import Node
import asyncio
from .config import BJ_TZ

class MetricsCollector:
    def __init__(self):
        self.collectors: Dict[str, threading.Thread] = {}
        self.collection_interval: int = 5
        self.last_errors: Dict[str, str] = {}
        self._columns_cache: Dict[str, set] = {}
        self._cluster_avg_inited: bool = False

    def set_collection_interval(self, interval: int):
        self.collection_interval = max(1, interval)

    def get_collectors_status(self) -> Dict[str, bool]:
        status = {}
        for cid, t in self.collectors.items():
            status[cid] = t.is_alive()
        return status
    
    def get_errors(self) -> Dict[str, str]:
        return dict(self.last_errors)

    def stop_all(self):
        for cid in list(self.collectors.keys()):
            self.stop(cid)

    def stop(self, collector_id: str):
        if collector_id in self.collectors:
            del self.collectors[collector_id]
        if collector_id in self.last_errors:
            del self.last_errors[collector_id]

    def start_for_nodes(self, nodes: List[Tuple[int, str, str, int]], interval: Optional[int] = None) -> Tuple[int, List[str]]:
        if interval:
            self.set_collection_interval(interval)
        started: List[str] = []
        for nid, hn, ip, cid in nodes:
            cid_str = f"{hn}"
            if cid_str in self.collectors and self.collectors[cid_str].is_alive():
                continue
            t = threading.Thread(target=self._collect_node_metrics, args=(nid, hn, ip, cid), name=f"metrics_{hn}", daemon=True)
            self.collectors[cid_str] = t
            t.start()
            started.append(hn)
        return len(started), started

    def _read_cpu_mem(self, node_name: str, ip: str) -> Tuple[float, float]:
        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
        out1, err1 = ssh_client.execute_command("cat /proc/stat | head -n 1")
        _time.sleep(0.5)
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
        return cpu_pct, mem_pct

    async def _save_metrics(self, node_id: int, hostname: str, cluster_id: int, cpu: float, mem: float):
        async with SessionLocal() as session:
            now = datetime.datetime.now(BJ_TZ)
            await session.execute(text("UPDATE nodes SET cpu_usage=:cpu, memory_usage=:mem, last_heartbeat=:hb WHERE id=:nid"), {"cpu": cpu, "mem": mem, "hb": now, "nid": node_id})
            await session.commit()

    def _collect_node_metrics(self, node_id: int, hostname: str, ip: str, cluster_id: int):
        cid = hostname
        while cid in self.collectors:
            try:
                cpu, mem = self._read_cpu_mem(hostname, ip)
                asyncio.run(self._save_metrics(node_id, hostname, cluster_id, cpu, mem))
            except Exception as e:
                self.last_errors[cid] = str(e)
            time.sleep(self.collection_interval)

    async def _get_table_columns(self, session: AsyncSession, table_name: str) -> set:
        if table_name in self._columns_cache:
            return self._columns_cache[table_name]
        res = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :t
        """), {"t": table_name})
        cols = set(r[0] for r in res.all())
        self._columns_cache[table_name] = cols
        return cols


metrics_collector = MetricsCollector()
