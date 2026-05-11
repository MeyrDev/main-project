"""
Модель отчёта.

Используется для хранения информации о сформированных отчетах:
карточка организации, сводка риска, портфельная аналитика и качество модели.
"""
import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReportType(str, enum.Enum):
    organization_card = "organization_card"
    risk_summary = "risk_summary"
    portfolio_analytics = "portfolio_analytics"
    model_quality = "model_quality"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    ready = "ready"
    failed = "failed"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    organization_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_by_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="report_type"),
        nullable=False,
        index=True,
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        default=ReportStatus.pending,
        nullable=False,
        index=True,
    )

    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organization = relationship("Organization", back_populates="reports")
    created_by = relationship("User", back_populates="reports")