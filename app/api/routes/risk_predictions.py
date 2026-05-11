"""
API для просмотра результатов прогнозирования риска.

Возвращает сохранённые risk_predictions, рассчитанные ML-модулем.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import RiskPrediction
from app.schemas import RiskPredictionItem

router = APIRouter(prefix="/risk-predictions", tags=["Risk predictions"])


@router.get("", response_model=list[RiskPredictionItem])
def get_risk_predictions(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = (
        select(RiskPrediction)
        .order_by(RiskPrediction.predicted_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(stmt).all()