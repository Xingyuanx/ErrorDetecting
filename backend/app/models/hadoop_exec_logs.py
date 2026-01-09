from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, TIMESTAMP, ForeignKey
from . import Base

class HadoopExecLog(Base):
    __tablename__ = "hadoop_exec_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cluster_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    end_time: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_user_id": self.from_user_id,
            "cluster_name": self.cluster_name,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
