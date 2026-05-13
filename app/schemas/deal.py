"""
Pydantic-схемы для сделок.

Сделки отражают коммерческие или финансовые взаимодействия
с хозяйствующими субъектами в CRM-системе.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.deal import DealStage


class DealCreate(BaseModel):
    owner_id: UUID | None = Field(
        default=None,
        description="Ответственный пользователь за сделку",
    )

    title: str = Field(
        min_length=2,
        max_length=255,
        description="Название сделки",
    )

    stage: DealStage = Field(
        default=DealStage.new,
        description="Стадия сделки",
    )

    amount: Decimal | None = Field(
        default=None,
        ge=0,
        description="Сумма сделки",
    )

    currency: str = Field(
        default="KZT",
        min_length=3,
        max_length=3,
        description="Валюта сделки",
    )

    expected_close_date: date | None = Field(
        default=None,
        description="Ожидаемая дата закрытия сделки",
    )

    description: str | None = Field(
        default=None,
        description="Описание сделки",
    )


class DealUpdate(BaseModel):
    owner_id: UUID | None = Field(default=None)
    title: str | None = Field(default=None, min_length=2, max_length=255)
    stage: DealStage | None = Field(default=None)
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    expected_close_date: date | None = Field(default=None)
    closed_at: datetime | None = Field(default=None)
    description: str | None = Field(default=None)


class DealItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    owner_id: UUID | None

    title: str
    stage: DealStage

    amount: Decimal | None
    currency: str

    expected_close_date: date | None
    closed_at: datetime | None
    description: str | None

    created_at: datetime
    updated_at: datetime