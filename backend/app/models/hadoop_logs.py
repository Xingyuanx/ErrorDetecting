from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, TIMESTAMP
from . import Base

class HadoopLog(Base):
    __tablename__ = "hadoop_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cluster_name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_host: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    info: Mapped[str | None] = mapped_column(Text, nullable=True)
    log_time: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id,
            "cluster_name": self.cluster_name,
            "node_host": self.node_host,
            "title": self.title,
            "info": self.info,
            "log_time": self.log_time.isoformat() if self.log_time else None,
        }
