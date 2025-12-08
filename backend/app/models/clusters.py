from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import TIMESTAMP
from app.models import Base

class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    type: Mapped[str] = mapped_column(String(50))
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    health_status: Mapped[str] = mapped_column(String(20), default="unknown")
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    config_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))

    def to_dict(self) -> dict:
        """将集群对象转换为可序列化字典。"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type,
            "node_count": self.node_count,
            "health_status": self.health_status,
            "description": self.description,
            "config_info": self.config_info,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }