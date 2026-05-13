"""
Pydantic-схемы для организаций.

Файл описывает входные данные для создания организации
и формат ответа API при получении карточки хозяйствующего субъекта.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    bin: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^\d{12}$",
        description="БИН организации, 12 цифр",
    )

    name: str = Field(
        min_length=2,
        max_length=255,
        description="Наименование организации",
    )

    industry: str | None = Field(
        default=None,
        max_length=120,
        description="Отрасль деятельности",
    )

    region: str | None = Field(
        default=None,
        max_length=120,
        description="Регион",
    )

    segment: str | None = Field(
        default=None,
        max_length=120,
        description="Сегмент бизнеса",
    )

    status: str = Field(
        default="active",
        max_length=50,
        description="Статус организации",
    )

    annual_revenue: Decimal | None = Field(
        default=None,
        ge=0,
        description="Годовая выручка",
    )

    employees_count: int | None = Field(
        default=None,
        ge=0,
        description="Количество сотрудников",
    )

    description: str | None = Field(
        default=None,
        description="Описание организации",
    )


class OrganizationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bin: str | None
    name: str
    industry: str | None
    region: str | None
    segment: str | None
    status: str
    annual_revenue: Decimal | None
    employees_count: int | None


class OrganizationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bin: str | None
    name: str
    industry: str | None
    region: str | None
    segment: str | None
    status: str
    annual_revenue: Decimal | None
    employees_count: int | None
    description: str | None
    created_at: datetime
    updated_at: datetime

class OrganizationUpdate(BaseModel):
    bin: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^\d{12}$",
        description="БИН организации, 12 цифр",
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Наименование организации",
    )

    industry: str | None = Field(
        default=None,
        max_length=120,
        description="Отрасль деятельности",
    )

    region: str | None = Field(
        default=None,
        max_length=120,
        description="Регион",
    )

    segment: str | None = Field(
        default=None,
        max_length=120,
        description="Сегмент бизнеса",
    )

    status: str | None = Field(
        default=None,
        max_length=50,
        description="Статус организации",
    )

    annual_revenue: Decimal | None = Field(
        default=None,
        ge=0,
        description="Годовая выручка",
    )

    employees_count: int | None = Field(
        default=None,
        ge=0,
        description="Количество сотрудников",
    )

    description: str | None = Field(
        default=None,
        description="Описание организации",
    )