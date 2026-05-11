"""
Модель результата прогнозирования риска.

Хранит рассчитанный risk_score, уровень риска, объяснение результата
и рекомендации для пользователя CRM-системы.
"""
import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    __table_args__ = (
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 1",
            name="ck_risk_predictions_score_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_snapshot_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("risk_feature_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    model_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ml_models.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    risk_score: Mapped[Decimal] = mapped_column(Numeric(6, 5), nullable=False)

    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level"),
        nullable=False,
        index=True,
    )

    explanation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    organization = relationship("Organization", back_populates="risk_predictions")
    feature_snapshot = relationship("RiskFeatureSnapshot", back_populates="risk_predictions")
    model = relationship("MLModel", back_populates="predictions")