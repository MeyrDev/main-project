"""
Модель хозяйствующего субъекта.

Организация представляет компанию для которого система хранит CRM-данные и рассчитывает уровень риска.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    bin: Mapped[str | None] = mapped_column(String(12), unique=True, nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    segment: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False, index=True)

    annual_revenue: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    employees_count: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contacts = relationship(
        "OrganizationContact",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    feature_snapshots = relationship(
        "RiskFeatureSnapshot",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    risk_predictions = relationship(
        "RiskPrediction",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    interactions = relationship(
        "Interaction",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    deals = relationship(
        "Deal",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    reports = relationship("Report", back_populates="organization")