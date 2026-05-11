"""
Модель ML-модели.

Хранит информацию о версии модели, алгоритме, пути к artifact-файлу,
метриках качества и параметрах обучения.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MLModel(Base):
    __tablename__ = "ml_models"

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_ml_model_name_version"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    algorithm_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    predictions = relationship("RiskPrediction", back_populates="model")