from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from . import Base

class SysExecLog(Base):
    __tablename__ = "sys_exec_logs"

    operation_id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    operation_time: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    def to_dict(self) -> dict:
        return {
            "operation_id": str(self.operation_id),
            "user_id": self.user_id,
            "description": self.description,
            "operation_time": self.operation_time.isoformat() if self.operation_time else None,
        }
