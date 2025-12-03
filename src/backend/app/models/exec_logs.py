from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TIMESTAMP, Text
from . import Base

class ExecLog(Base):
    __tablename__ = "exec_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    exec_id: Mapped[str] = mapped_column(String(32), unique=True)
    fault_id: Mapped[str] = mapped_column(String(32))
    command_type: Mapped[str] = mapped_column(String(50))
    script_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    command_content: Mapped[str] = mapped_column(Text)
    target_nodes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    execution_status: Mapped[str] = mapped_column(String(20), default="pending")
    start_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operator: Mapped[str] = mapped_column(String(50), default="system")
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))

    def to_dict(self) -> dict:
        """将执行日志转换为可序列化字典。"""
        return {
            "exec_id": self.exec_id,
            "fault_id": self.fault_id,
            "command_type": self.command_type,
            "execution_status": self.execution_status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "exit_code": self.exit_code,
        }