from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class RiskLevelCount(BaseModel):
    risk_level: str
    count: int


class DashboardHighRiskOrganization(BaseModel):
    organization_id: UUID
    organization_name: str
    industry: str | None
    region: str | None
    risk_score: Decimal
    risk_level: str
    predicted_at: datetime


class DashboardRecentPrediction(BaseModel):
    prediction_id: UUID
    organization_id: UUID
    organization_name: str
    risk_score: Decimal
    risk_level: str
    predicted_at: datetime


class DashboardRecentAuditLog(BaseModel):
    id: UUID
    action: str
    entity_type: str | None
    entity_id: UUID | None
    details: dict | None
    created_at: datetime


class DashboardSummary(BaseModel):
    organizations_count: int
    users_count: int
    deals_count: int
    predictions_count: int

    risk_distribution: list[RiskLevelCount]
    high_risk_organizations: list[DashboardHighRiskOrganization]
    recent_predictions: list[DashboardRecentPrediction]
    recent_audit_logs: list[DashboardRecentAuditLog]