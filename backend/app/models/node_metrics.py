from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, TIMESTAMP
from . import Base

class NodeMetric(Base):
    __tablename__ = "node_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column()
    node_id: Mapped[int] = mapped_column()
    hostname: Mapped[str] = mapped_column(String(100))
    cpu_usage: Mapped[float] = mapped_column(Float)
    memory_usage: Mapped[float] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
