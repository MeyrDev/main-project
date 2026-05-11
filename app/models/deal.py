"""
Модель сделки.

Сделка отражает коммерческое или финансовое взаимодействие с организацией.
Она нужна для CRM-части системы и может учитываться при анализе риска.
"""
import enum
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DealStage(str, enum.Enum):
    new = "new"
    negotiation = "negotiation"
    approved = "approved"
    rejected = "rejected"
    closed = "closed"


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    stage: Mapped[DealStage] = mapped_column(
        Enum(DealStage, name="deal_stage"),
        default=DealStage.new,
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="KZT", nullable=False)

    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

    organization = relationship("Organization", back_populates="deals")
    owner = relationship("User", back_populates="owned_deals")
    interactions = relationship("Interaction", back_populates="deal")