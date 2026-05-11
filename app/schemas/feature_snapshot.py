"""
Pydantic-схемы для признаков риска.

Определяют формат JSON, который пользователь отправляет при добавлении
финансово-операционных признаков организации.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RiskFeatureSnapshotCreate(BaseModel):
    period_date: date

    revenue: Decimal | None = None
    debt_amount: Decimal | None = None

    overdue_days_30: int = 0
    overdue_days_90: int = 0
    disputes_count: int = 0
    transactions_count: int = 0

    employees_count: int | None = None
    raw_features: dict | None = None


class RiskFeatureSnapshotItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    import_batch_id: UUID | None

    period_date: date

    revenue: Decimal | None
    debt_amount: Decimal | None

    overdue_days_30: int
    overdue_days_90: int
    disputes_count: int
    transactions_count: int

    employees_count: int | None
    raw_features: dict | None

    created_at: datetime