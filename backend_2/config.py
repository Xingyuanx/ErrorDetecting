from pydantic_settings import BaseSettings
from typing import Dict, Tuple
from dotenv import load_dotenv
import os

# Load environment variables from .env file
print(f"Current working directory: {os.getcwd()}")
print(f"Loading .env from: {os.path.join(os.getcwd(), '.env')}")
load_dotenv()

# Parse hadoop nodes from environment variables at module level
HADOOP_NODES = {}
print("\n=== Parsing Node Configurations ===")
for key, value in os.environ.items():
    if key.startswith("NODE_"):
        print(f"  - Found: {key} = {value}")
        node_name = key.replace("NODE_", "").lower()
        ip, username, password = value.split(",")
        HADOOP_NODES[node_name] = (ip, username, password)

class Settings(BaseSettings):
    # Hadoop Cluster Configuration
    hadoop_home: str = os.getenv("HADOOP_HOME", "/opt/module/hadoop-3.1.3")
    log_dir: str = os.getenv("LOG_DIR", "/opt/module/hadoop-3.1.3/logs")
    
    # SSH Configuration
    ssh_port: int = int(os.getenv("SSH_PORT", "22"))
    ssh_timeout: int = int(os.getenv("SSH_TIMEOUT", "10"))
    
    # Hadoop Nodes Configuration
    @property
    def hadoop_nodes(self) -> Dict[str, Tuple[str, str, str]]:
        """Get parsed hadoop nodes"""
        return HADOOP_NODES

# Create settings instance
settings = Settings()