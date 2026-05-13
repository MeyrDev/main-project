"""
Pydantic-схемы для признаков риска.

Файл описывает формат входных и выходных данных для risk_feature_snapshots.
Эти признаки используются ML-моделью для расчёта риска организации.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RiskFeatureSnapshotCreate(BaseModel):
    period_date: date = Field(
        description="Дата периода, за который фиксируются признаки риска"
    )

    revenue: Decimal | None = Field(
        default=None,
        ge=0,
        description="Выручка организации за период",
    )

    debt_amount: Decimal | None = Field(
        default=None,
        ge=0,
        description="Сумма задолженности организации",
    )

    overdue_days_30: int = Field(
        default=0,
        ge=0,
        description="Количество дней просрочки в окне 30 дней",
    )

    overdue_days_90: int = Field(
        default=0,
        ge=0,
        description="Количество дней просрочки в окне 90 дней",
    )

    disputes_count: int = Field(
        default=0,
        ge=0,
        description="Количество спорных ситуаций",
    )

    transactions_count: int = Field(
        default=0,
        ge=0,
        description="Количество транзакций за период",
    )

    employees_count: int | None = Field(
        default=None,
        ge=0,
        description="Количество сотрудников организации",
    )

    raw_features: dict | None = Field(
        default=None,
        description="Дополнительные необработанные признаки",
    )


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