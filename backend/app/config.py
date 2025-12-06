import os
from dotenv import load_dotenv

load_dotenv()

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

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
