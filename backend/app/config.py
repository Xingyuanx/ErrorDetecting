import os
from dotenv import load_dotenv
from typing import Dict, Tuple

load_dotenv()

# Database Configuration
_db_url = os.getenv("DATABASE_URL")
if not _db_url:
    _host = os.getenv("DB_HOST")
    _port = os.getenv("DB_PORT")
    _name = os.getenv("DB_NAME")
    _user = os.getenv("DB_USER")
    _password = os.getenv("DB_PASSWORD")
    if all([_host, _port, _name, _user, _password]):
        _db_url = f"postgresql+asyncpg://{_user}:{_password}@{_host}:{_port}/{_name}"
    else:
        _db_url = "postgresql+asyncpg://postgres:password@localhost:5432/hadoop_fault_db"

DATABASE_URL = _db_url

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Hadoop Cluster Configuration
HADOOP_HOME = os.getenv("HADOOP_HOME", "/opt/module/hadoop-3.1.3")
LOG_DIR = os.getenv("LOG_DIR", "/opt/module/hadoop-3.1.3/logs")

# SSH Configuration
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_TIMEOUT = int(os.getenv("SSH_TIMEOUT", "10"))

# Hadoop Nodes Configuration
# Parse hadoop nodes from environment variables at module level
HADOOP_NODES = {}
for key, value in os.environ.items():
    if key.startswith("NODE_"):
        node_name = key.replace("NODE_", "").lower()
        if "," in value:
            ip, username, password = value.split(",")
            HADOOP_NODES[node_name] = (ip, username, password)

# Static node configuration as fallback
if not HADOOP_NODES:
    HADOOP_NODES = {
        "hadoop102": ("192.168.10.102", "hadoop", "limouren..."),
        "hadoop103": ("192.168.10.103", "hadoop", "limouren..."),
        "hadoop104": ("192.168.10.104", "hadoop", "limouren..."),
        "hadoop105": ("192.168.10.105", "hadoop", "limouren..."),
        "hadoop100": ("192.168.10.100", "hadoop", "limouren...")
    }

# Aliases for backward compatibility with backend_2 code
hadoop_home = HADOOP_HOME
log_dir = LOG_DIR
ssh_port = SSH_PORT
ssh_timeout = SSH_TIMEOUT
hadoop_nodes = HADOOP_NODES
