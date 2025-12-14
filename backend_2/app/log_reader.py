from typing import List, Dict, Optional
from config import settings
from app.ssh_utils import ssh_manager
import os

class LogReader:
    """Log Reader for Hadoop cluster nodes"""
    
    def __init__(self):
        self.log_dir = settings.log_dir
    
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
    
    def read_log(self, node_name: str, log_type: str) -> str:
        """Read log from a specific node"""
        # Get log file path
        log_file_path = self.get_log_file_path(node_name, log_type)
        
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name)
        
        # Read log file content
        return ssh_client.read_file(log_file_path)
    
    def read_all_nodes_log(self, log_type: str) -> Dict[str, str]:
        """Read log from all nodes"""
        logs = {}
        
        for node_name in settings.hadoop_nodes:
            try:
                logs[node_name] = self.read_log(node_name, log_type)
            except Exception as e:
                logs[node_name] = f"Error reading log: {str(e)}"
        
        return logs
    
    def save_log_to_local(self, node_name: str, log_type: str, local_file_path: str) -> None:
        """Save log from a specific node to local file"""
        # Get log file path
        log_file_path = self.get_log_file_path(node_name, log_type)
        
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name)
        
        # Download log file to local
        ssh_client.download_file(log_file_path, local_file_path)
    
    def save_all_nodes_log(self, log_type: str, local_dir: str = ".") -> List[str]:
        """Save logs from all nodes to local directory"""
        saved_files = []
        
        # Create local directory if it doesn't exist
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        
        for node_name in settings.hadoop_nodes:
            try:
                # Generate local file path
                local_file_path = os.path.join(local_dir, f"{node_name}_{log_type}.log")
                # Save log to local file
                self.save_log_to_local(node_name, log_type, local_file_path)
                saved_files.append(local_file_path)
            except Exception as e:
                print(f"Error saving log from {node_name}: {str(e)}")
        
        return saved_files
    
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
    
    def get_log_files_list(self, node_name: str) -> List[str]:
        """Get list of log files on a specific node"""
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name)
        
        # Execute command to list log files
        stdout, stderr = ssh_client.execute_command(f"ls -la {self.log_dir}")
        
        # Parse log files from output
        log_files = []
        if not stderr:
            for line in stdout.splitlines():
                if '.log' in line:
                    # Extract file name
                    parts = line.split()
                    if parts:
                        log_files.append(parts[-1])
        
        return log_files
    
    def check_log_file_exists(self, node_name: str, log_type: str) -> bool:
        """Check if log file exists on a specific node"""
        # Get log file path
        log_file_path = self.get_log_file_path(node_name, log_type)
        
        # Get SSH connection
        ssh_client = ssh_manager.get_connection(node_name)
        
        try:
            # Execute command to check if file exists
            stdout, stderr = ssh_client.execute_command(f"ls -la {log_file_path} 2>/dev/null")
            return bool(stdout.strip())
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

# Create a global LogReader instance
log_reader = LogReader()