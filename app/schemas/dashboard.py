from pydantic import BaseModel


class RiskLevelCount(BaseModel):
    risk_level: str
    count: int


class DashboardSummary(BaseModel):
    organizations_count: int
    users_count: int
    deals_count: int
    predictions_count: int
    risk_distribution: list[RiskLevelCount]