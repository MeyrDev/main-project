from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RiskPredictionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    feature_snapshot_id: UUID | None
    model_id: UUID | None
    risk_score: Decimal
    risk_level: str
    explanation: dict | None
    recommendations: dict | None
    predicted_at: datetime


class OrganizationRiskResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    risk_prediction: RiskPredictionItem | None