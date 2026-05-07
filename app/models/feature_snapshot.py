from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskFeatureSnapshot(Base):
    __tablename__ = "risk_feature_snapshots"

    __table_args__ = (
        UniqueConstraint("organization_id", "period_date", name="uq_risk_feature_snapshot_period"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    import_batch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("data_import_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    period_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    revenue: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    debt_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    overdue_days_30: Mapped[int] = mapped_column(default=0, nullable=False)
    overdue_days_90: Mapped[int] = mapped_column(default=0, nullable=False)
    disputes_count: Mapped[int] = mapped_column(default=0, nullable=False)
    transactions_count: Mapped[int] = mapped_column(default=0, nullable=False)

    employees_count: Mapped[int | None] = mapped_column(nullable=True)

    raw_features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organization = relationship("Organization", back_populates="feature_snapshots")
    import_batch = relationship("DataImportBatch", back_populates="feature_snapshots")
    risk_predictions = relationship("RiskPrediction", back_populates="feature_snapshot")