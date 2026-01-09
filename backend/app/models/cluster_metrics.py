from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, TIMESTAMP
from . import Base

class ClusterMetric(Base):
    __tablename__ = "cluster_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column()
    cluster_name: Mapped[str] = mapped_column(String(100))
    cpu_avg: Mapped[float] = mapped_column(Float)
    memory_avg: Mapped[float] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True))
