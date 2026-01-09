import os
import socket
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

DEFAULT_SSH_USER = os.getenv("HADOOP_USER", "hadoop")
DEFAULT_SSH_PASSWORD = os.getenv("HADOOP_PASSWORD", "limouren...")

class SSHClient:
    """SSH Client for connecting to remote servers"""
    
    def __init__(self, hostname: str, username: str, password: str, port: int = SSH_PORT):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None
    
    def _ensure_connected(self) -> None:
        if self.client is None:
            self.connect()
            return
        try:
            transport = self.client.get_transport()
            if transport is None or not transport.is_active():
                self.connect()
        except Exception:
            self.connect()
    
    def connect(self) -> None:
        """Establish SSH connection"""
        self.client = paramiko.SSHClient()
        # Automatically add host keys
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sock = None
        socks5 = os.getenv("TS_SOCKS5_SERVER") or os.getenv("TAILSCALE_SOCKS5_SERVER")
        if socks5:
            try:
                sock = _socks5_connect(socks5, self.hostname, self.port, SSH_TIMEOUT)
            except Exception:
                sock = None
        self.client.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
            timeout=SSH_TIMEOUT,
            sock=sock,
        )
    
    def execute_command(self, command: str) -> tuple:
        """Execute command on remote server"""
        self._ensure_connected()
        
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def execute_command_with_status(self, command: str) -> tuple:
        self._ensure_connected()
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()
    
    def execute_command_with_timeout(self, command: str, timeout: int = 30) -> tuple:
        """Execute command with timeout"""
        self._ensure_connected()
        
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        return stdout.read().decode(), stderr.read().decode()

    def execute_command_with_timeout_and_status(self, command: str, timeout: int = 30) -> tuple:
        self._ensure_connected()
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()
    
    def read_file(self, file_path: str) -> str:
        """Read file content from remote server"""
        self._ensure_connected()
        
        with self.client.open_sftp() as sftp:
            with sftp.open(file_path, 'r') as f:
                return f.read().decode()
    
    def download_file(self, remote_path: str, local_path: str) -> None:
        """Download file from remote server to local"""
        self._ensure_connected()
        
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
    
    def get_connection(self, node_name: str, ip: str = None, username: str = None, password: str = None) -> SSHClient:
        """Get or create SSH connection for a node"""
        if node_name in self.connections:
            client = self.connections[node_name]
            if ip and getattr(client, "hostname", None) != ip:
                try:
                    client.close()
                except Exception:
                    pass
                del self.connections[node_name]
            elif username and getattr(client, "username", None) != username:
                try:
                    client.close()
                except Exception:
                    pass
                del self.connections[node_name]
            elif password and getattr(client, "password", None) != password:
                try:
                    client.close()
                except Exception:
                    pass
                del self.connections[node_name]

        if node_name not in self.connections:
            if not ip:
                raise ValueError(f"IP address required for new connection to {node_name}")

            _user = username or DEFAULT_SSH_USER
            _pass = password or DEFAULT_SSH_PASSWORD

            client = SSHClient(ip, _user, _pass)
            self.connections[node_name] = client

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


def _parse_hostport(value: str, default_port: int) -> tuple[str, int]:
    s = (value or "").strip()
    if not s:
        return ("127.0.0.1", default_port)
    if s.startswith("http://"):
        s = s[7:]
    if s.startswith("socks5://"):
        s = s[9:]
    if "/" in s:
        s = s.split("/", 1)[0]
    if ":" in s:
        host, port_s = s.rsplit(":", 1)
        try:
            return (host.strip() or "127.0.0.1", int(port_s.strip()))
        except Exception:
            return (host.strip() or "127.0.0.1", default_port)
    return (s, default_port)


def _socks5_connect(proxy: str, dest_host: str, dest_port: int, timeout: int) -> socket.socket:
    proxy_host, proxy_port = _parse_hostport(proxy, 1080)
    s = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    s.settimeout(timeout)
    s.sendall(b"\x05\x01\x00")
    resp = s.recv(2)
    if len(resp) != 2 or resp[0] != 0x05 or resp[1] != 0x00:
        s.close()
        raise RuntimeError("socks5_auth_failed")
    atyp = 0x03
    addr = dest_host.encode("utf-8")
    try:
        packed = socket.inet_pton(socket.AF_INET, dest_host)
        atyp = 0x01
        addr_field = packed
    except Exception:
        try:
            packed6 = socket.inet_pton(socket.AF_INET6, dest_host)
            atyp = 0x04
            addr_field = packed6
        except Exception:
            if len(addr) > 255:
                s.close()
                raise RuntimeError("socks5_domain_too_long")
            addr_field = bytes([len(addr)]) + addr
    port_field = int(dest_port).to_bytes(2, "big", signed=False)
    req = b"\x05\x01\x00" + bytes([atyp]) + addr_field + port_field
    s.sendall(req)
    head = s.recv(4)
    if len(head) != 4 or head[0] != 0x05:
        s.close()
        raise RuntimeError("socks5_bad_reply")
    rep = head[1]
    if rep != 0x00:
        s.close()
        raise RuntimeError(f"socks5_connect_failed:{rep}")
    bnd_atyp = head[3]
    if bnd_atyp == 0x01:
        s.recv(4)
    elif bnd_atyp == 0x04:
        s.recv(16)
    elif bnd_atyp == 0x03:
        ln = s.recv(1)
        if ln:
            s.recv(ln[0])
    s.recv(2)
    return s
