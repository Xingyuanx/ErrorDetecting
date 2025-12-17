import paramiko
from typing import Optional, TextIO, Dict, Tuple
from .config import SSH_PORT, SSH_TIMEOUT

# Create a static node configuration dictionary that will be used for all requests
# This avoids the issue of environment variables not being available in child processes
STATIC_NODE_CONFIG = {
    "hadoop102": ("192.168.10.102", "hadoop", "limouren..."),
    "hadoop103": ("192.168.10.103", "hadoop", "limouren..."),
    "hadoop104": ("192.168.10.104", "hadoop", "limouren..."),
    "hadoop105": ("192.168.10.105", "hadoop", "limouren..."),
    "hadoop100": ("192.168.10.100", "hadoop", "limouren...")
}

class SSHClient:
    """SSH Client for connecting to remote servers"""
    
    def __init__(self, hostname: str, username: str, password: str, port: int = SSH_PORT):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None
    
    def connect(self) -> None:
        """Establish SSH connection"""
        self.client = paramiko.SSHClient()
        # Automatically add host keys
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the server
        self.client.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
            timeout=SSH_TIMEOUT
        )
    
    def execute_command(self, command: str) -> tuple:
        """Execute command on remote server"""
        if not self.client:
            self.connect()
        
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
    
    def execute_command_with_timeout(self, command: str, timeout: int = 30) -> tuple:
        """Execute command with timeout"""
        if not self.client:
            self.connect()
        
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        return stdout.read().decode(), stderr.read().decode()
    
    def read_file(self, file_path: str) -> str:
        """Read file content from remote server"""
        if not self.client:
            self.connect()
        
        with self.client.open_sftp() as sftp:
            with sftp.open(file_path, 'r') as f:
                return f.read().decode()
    
    def download_file(self, remote_path: str, local_path: str) -> None:
        """Download file from remote server to local"""
        if not self.client:
            self.connect()
        
        with self.client.open_sftp() as sftp:
            sftp.get(remote_path, local_path)
    
    def close(self) -> None:
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

class SSHConnectionManager:
    """SSH Connection Manager for managing multiple SSH connections"""
    
    def __init__(self):
        self.connections = {}
    
    def get_connection(self, node_name: str) -> SSHClient:
        """Get or create SSH connection for a node"""
        if node_name not in self.connections:
            # Get node configuration from static config instead of settings
            if node_name not in STATIC_NODE_CONFIG:
                raise ValueError(f"Node {node_name} not configured")
            
            ip, username, password = STATIC_NODE_CONFIG[node_name]
            self.connections[node_name] = SSHClient(ip, username, password)
        
        return self.connections[node_name]
    
    def close_all(self) -> None:
        """Close all SSH connections"""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()

# Create a global SSH connection manager instance
ssh_manager = SSHConnectionManager()