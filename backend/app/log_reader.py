from typing import List, Dict, Optional
from .config import LOG_DIR
from .ssh_utils import ssh_manager

class LogReader:
    """Log Reader for Hadoop cluster nodes"""
    
    def __init__(self):
        self.log_dir = LOG_DIR
        self._node_log_dir: Dict[str, str] = {}
        self._candidates = [
            "/usr/local/hadoop/logs",
            "/opt/hadoop/logs",
            "/usr/local/hadoop-3.3.6/logs",
            "/usr/local/hadoop-3.3.5/logs",
            "/usr/local/hadoop-3.1.3/logs",
            "/opt/module/hadoop-3.1.3/logs",
            "/var/log/hadoop",
        ]
    
    def get_log_file_path(self, node_name: str, log_type: str) -> str:
        """Generate log file path based on node name and log type"""
        # Map log type to actual log file name
        log_file_map = {
            "namenode": "hadoop-hadoop-namenode",
            "datanode": "hadoop-hadoop-datanode",
            "resourcemanager": "hadoop-hadoop-resourcemanager",
            "nodemanager": "hadoop-hadoop-nodemanager",
            "historyserver": "hadoop-hadoop-historyserver"
        }
        
        # Get the base log file name
        base_name = log_file_map.get(log_type.lower(), log_type.lower())
        # Generate full log file path
        return f"{self.log_dir}/{base_name}-{node_name.replace('_', '')}.log"
    
    def read_log(self, node_name: str, log_type: str, ip: str) -> str:
        """Read log from a specific node"""
        # Ensure working log dir
        self.find_working_log_dir(node_name, ip)
        paths = self.get_log_file_paths(node_name, log_type)
        
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
        
        # Read log file content
        # try direct candidates
        for p in paths:
            out, err = ssh_client.execute_command(f"ls -la {p} 2>/dev/null")
            if not err and out.strip():
                out, err = ssh_client.execute_command(f"cat {p} 2>/dev/null")
                if not err:
                    return out
        # resolve by directory listing
        base_dir = self._node_log_dir.get(node_name, self.log_dir)
        out, err = ssh_client.execute_command(f"ls -la {base_dir} 2>/dev/null")
        if not err and out.strip():
            for line in out.splitlines():
                parts = line.split()
                if parts:
                    fn = parts[-1]
                    lf = fn.lower()
                    if log_type in lf and node_name in lf and (lf.endswith(".log") or lf.endswith(".out") or lf.endswith(".out.1")):
                        out2, err2 = ssh_client.execute_command(f"cat {base_dir}/{fn} 2>/dev/null")
                        if not err2:
                            return out2
        raise FileNotFoundError("No such file")
    
    def read_all_nodes_log(self, nodes: List[Dict[str, str]], log_type: str) -> Dict[str, str]:
        """Read log from all nodes"""
        logs = {}
        
        for node in nodes:
            node_name = node['name']
            ip = node.get('ip')
            if not ip:
                logs[node_name] = "Error: IP address not found"
                continue
                
            try:
                logs[node_name] = self.read_log(node_name, log_type, ip)
            except Exception as e:
                logs[node_name] = f"Error reading log: {str(e)}"
        
        return logs
    
    def filter_log_by_date(self, log_content: str, start_date: str, end_date: str) -> str:
        """Filter log content by date range"""
        filtered_lines = []
        for line in log_content.splitlines():
            # Check if line contains date in the format [YYYY-MM-DD HH:MM:SS,mmm]
            if line.startswith('['):
                # Extract date part
                date_str = line[1:11]  # Get YYYY-MM-DD part
                if start_date <= date_str <= end_date:
                    filtered_lines.append(line)
        return '\n'.join(filtered_lines)
    
    def get_log_files_list(self, node_name: str, ip: Optional[str] = None) -> List[str]:
        """Get list of log files on a specific node"""
        # Ensure working log dir
        if ip:
            self.find_working_log_dir(node_name, ip)
        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
        
        # Execute command to list log files from available directories
        dirs = [self._node_log_dir.get(node_name, self.log_dir)] + self._candidates
        stdout = ""
        for d in dirs:
            out, err = ssh_client.execute_command(f"ls -1 {d} 2>/dev/null")
            if not err and out.strip():
                stdout = out
                self._node_log_dir[node_name] = d
                break
        stderr = ""
        
        # Parse log files from output
        log_files = []
        if not stderr and stdout.strip():
            for line in stdout.splitlines():
                name = line.strip()
                if name.endswith(".log") or name.endswith(".out") or name.endswith(".out.1"):
                    log_files.append(name)
        
        return log_files
    
    def check_log_file_exists(self, node_name: str, log_type: str, ip: Optional[str] = None) -> bool:
        """Check if log file exists on a specific node"""
        # Ensure working log dir
        if ip:
            self.find_working_log_dir(node_name, ip)
        paths = self.get_log_file_paths(node_name, log_type)
        
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
        
        try:
            # Execute command to check if file exists
            for p in paths:
                stdout, stderr = ssh_client.execute_command(f"ls -la {p} 2>/dev/null")
                if not stderr and stdout.strip():
                    return True
            base_dir = self._node_log_dir.get(node_name, self.log_dir)
            stdout, stderr = ssh_client.execute_command(f"ls -la {base_dir} 2>/dev/null")
            if not stderr and stdout.strip():
                for line in stdout.splitlines():
                    parts = line.split()
                    if parts:
                        fn = parts[-1].lower()
                        if log_type in fn and node_name in fn and (fn.endswith(".log") or fn.endswith(".out") or fn.endswith(".out.1")):
                            return True
            return False
        except Exception as e:
            print(f"Error checking log file existence: {e}")
            return False
    
    def get_node_services(self, node_name: str) -> List[str]:
        """Get list of running services on a node based on log files"""
        # Get all log files
        log_files = self.get_log_files_list(node_name)
        
        # Extract service types from log file names
        services = []
        for log_file in log_files:
            if "namenode" in log_file:
                services.append("namenode")
            elif "datanode" in log_file:
                services.append("datanode")
            elif "resourcemanager" in log_file:
                services.append("resourcemanager")
            elif "nodemanager" in log_file:
                services.append("nodemanager")
            elif "secondarynamenode" in log_file:
                services.append("secondarynamenode")
        
        # Remove duplicates
        return list(set(services))

    def find_working_log_dir(self, node_name: str, ip: str) -> str:
        """Detect a working log directory on remote node and set it"""
        ssh_client = ssh_manager.get_connection(node_name, ip=ip)
        # try current
        current = self._node_log_dir.get(node_name, self.log_dir)
        stdout, stderr = ssh_client.execute_command(f"ls -la {current}")
        if not stderr and stdout.strip():
            self._node_log_dir[node_name] = current
            return current
        for d in [current] + self._candidates:
            stdout, stderr = ssh_client.execute_command(f"ls -la {d} 2>/dev/null")
            if not stderr and stdout.strip():
                self._node_log_dir[node_name] = d
                return d
        self._node_log_dir[node_name] = self.log_dir
        return self._node_log_dir[node_name]

    def get_log_file_paths(self, node_name: str, log_type: str) -> List[str]:
        base_dir = self._node_log_dir.get(node_name, self.log_dir)
        base = f"{base_dir}/hadoop-hadoop-{log_type}-{node_name}"
        return [f"{base}.log", f"{base}.out", f"{base}.out.1"]

# Create a global LogReader instance
log_reader = LogReader()
