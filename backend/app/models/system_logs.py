from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from sqlalchemy import TIMESTAMP, Text
from . import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    log_id: Mapped[str] = mapped_column(String(32), unique=True)
    fault_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cluster_id: Mapped[int | None] = mapped_column(nullable=True)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    host: Mapped[str] = mapped_column(String(100))
    service: Mapped[str] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    log_level: Mapped[str] = mapped_column(String(10))
    message: Mapped[str] = mapped_column(Text)
    exception: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))

    def to_dict(self) -> dict:
        """将系统日志转换为可序列化字典。"""
        return {
            "log_id": self.log_id,
            "cluster_id": self.cluster_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "service": self.service,
            "source": self.source,
            "log_level": self.log_level,
            "message": self.message,
            "processed": self.processed,
        }
