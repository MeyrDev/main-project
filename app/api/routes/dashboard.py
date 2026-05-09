from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Deal, Organization, RiskPrediction, User
from app.schemas import DashboardSummary, RiskLevelCount

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    organizations_count = db.scalar(select(func.count()).select_from(Organization)) or 0
    users_count = db.scalar(select(func.count()).select_from(User)) or 0
    deals_count = db.scalar(select(func.count()).select_from(Deal)) or 0
    predictions_count = db.scalar(select(func.count()).select_from(RiskPrediction)) or 0

    distribution_stmt = (
        select(RiskPrediction.risk_level, func.count(RiskPrediction.id))
        .group_by(RiskPrediction.risk_level)
        .order_by(RiskPrediction.risk_level)
    )

    risk_distribution = [
        RiskLevelCount(risk_level=str(level.value), count=count)
        for level, count in db.execute(distribution_stmt).all()
    ]

    return DashboardSummary(
        organizations_count=organizations_count,
        users_count=users_count,
        deals_count=deals_count,
        predictions_count=predictions_count,
        risk_distribution=risk_distribution,
    )