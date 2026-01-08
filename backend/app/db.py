from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import DATABASE_URL, APP_TIMEZONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"server_settings": {"timezone": APP_TIMEZONE}},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncSession:
    """获取一个异步数据库会话，用于依赖注入。"""
    async with SessionLocal() as session:
        yield session
