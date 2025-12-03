from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TIMESTAMP
from app.models import Base

class FaultRecord(Base):
    __tablename__ = "fault_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    fault_id: Mapped[str] = mapped_column(String(32), unique=True)
    cluster_id: Mapped[int | None] = mapped_column(nullable=True)
    fault_type: Mapped[str] = mapped_column(String(50))
    fault_level: Mapped[str] = mapped_column(String(20), default="medium")
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_nodes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    affected_clusters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(String, nullable=True)
    repair_suggestion: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="detected")
    assignee: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reporter: Mapped[str] = mapped_column(String(50), default="system")
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    resolved_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        """将故障记录转换为可序列化字典。"""
        return {
            "fault_id": self.fault_id,
            "cluster_id": self.cluster_id,
            "fault_type": self.fault_type,
            "fault_level": self.fault_level,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }