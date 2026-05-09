from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import (
    MLModel,
    Organization,
    RiskFeatureSnapshot,
    RiskLevel,
    RiskPrediction,
)
from app.schemas import RiskPredictionItem

router = APIRouter(prefix="/ml", tags=["ML"])


def calculate_demo_risk_score(snapshot: RiskFeatureSnapshot) -> Decimal:
    revenue = float(snapshot.revenue or 0)
    debt = float(snapshot.debt_amount or 0)

    debt_ratio = debt / revenue if revenue > 0 else 1.0

    score = 0.0

    score += min(debt_ratio, 1.0) * 0.35
    score += min(snapshot.overdue_days_30 / 60, 1.0) * 0.20
    score += min(snapshot.overdue_days_90 / 90, 1.0) * 0.25
    score += min(snapshot.disputes_count / 10, 1.0) * 0.15

    if snapshot.transactions_count < 50:
        score += 0.05

    score = max(0.0, min(score, 1.0))

    return Decimal(str(round(score, 5)))


def define_risk_level(score: Decimal) -> RiskLevel:
    value = float(score)

    if value < 0.25:
        return RiskLevel.low

    if value < 0.55:
        return RiskLevel.medium

    if value < 0.80:
        return RiskLevel.high

    return RiskLevel.critical


@router.post("/predict/{organization_id}", response_model=RiskPredictionItem)
def predict_organization_risk(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    snapshot_stmt = (
        select(RiskFeatureSnapshot)
        .where(RiskFeatureSnapshot.organization_id == organization_id)
        .order_by(RiskFeatureSnapshot.period_date.desc())
        .limit(1)
    )

    snapshot = db.scalars(snapshot_stmt).first()

    if snapshot is None:
        raise HTTPException(
            status_code=400,
            detail="No risk feature snapshot found for this organization",
        )

    model = db.scalar(
        select(MLModel)
        .where(MLModel.name == "demo_rule_based_model")
        .where(MLModel.version == "1.0.0")
    )

    if model is None:
        model = MLModel(
            name="demo_rule_based_model",
            version="1.0.0",
            algorithm_name="RuleBasedScoring",
            target_name="risk_score",
            artifact_path=None,
            metrics={
                "description": "Temporary rule-based model before ML integration"
            },
            parameters={
                "debt_ratio_weight": 0.35,
                "overdue_30_weight": 0.20,
                "overdue_90_weight": 0.25,
                "disputes_weight": 0.15,
                "low_transactions_penalty": 0.05,
            },
        )
        db.add(model)
        db.flush()

    risk_score = calculate_demo_risk_score(snapshot)
    risk_level = define_risk_level(risk_score)

    prediction = RiskPrediction(
        organization_id=organization.id,
        feature_snapshot_id=snapshot.id,
        model_id=model.id,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation={
            "method": "demo_rule_based_scoring",
            "factors": {
                "revenue": str(snapshot.revenue),
                "debt_amount": str(snapshot.debt_amount),
                "overdue_days_30": snapshot.overdue_days_30,
                "overdue_days_90": snapshot.overdue_days_90,
                "disputes_count": snapshot.disputes_count,
                "transactions_count": snapshot.transactions_count,
            },
        },
        recommendations={
            "actions": [
                "проверить финансовую отчетность",
                "проанализировать просроченную задолженность",
                "оценить историю взаимодействий и спорных ситуаций",
            ]
        },
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction