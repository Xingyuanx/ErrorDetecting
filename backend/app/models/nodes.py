from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy import TIMESTAMP, Float
from . import Base

class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), unique=True)
    cluster_id: Mapped[int] = mapped_column()
    hostname: Mapped[str] = mapped_column(String(100))
    ip_address: Mapped[str] = mapped_column(INET)
    ssh_user: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ssh_password: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="unknown")
    cpu_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    disk_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_heartbeat: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
