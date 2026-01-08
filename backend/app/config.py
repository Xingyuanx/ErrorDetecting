import os
import json
from dotenv import load_dotenv
from typing import Dict, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

# Timezone Configuration
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Shanghai")
BJ_TZ = ZoneInfo(APP_TIMEZONE)

def now_bj() -> datetime:
    return datetime.now(BJ_TZ)

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
SYNC_DATABASE_URL = _db_url.replace("postgresql+asyncpg://", "postgresql://")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


# SSH Configuration
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_TIMEOUT = int(os.getenv("SSH_TIMEOUT", "10"))

ssh_port = SSH_PORT
ssh_timeout = SSH_TIMEOUT

LOG_DIR = os.getenv("HADOOP_LOG_DIR", "/usr/local/hadoop/logs")
