from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.ml.predictor import ARTIFACT_PATH, load_artifact, predict_risk
from app.models import (
    MLModel,
    Organization,
    RiskFeatureSnapshot,
    RiskPrediction,
)
from app.schemas import MLModelInfo, RiskPredictionItem
from app.services.audit import create_audit_log

router = APIRouter(prefix="/ml", tags=["ML"])

@router.get("/model-info", response_model=MLModelInfo)
def get_model_info():
    if not ARTIFACT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="ML model artifact not found. Run: python -m app.ml.train_model",
        )

    artifact = load_artifact()

    return MLModelInfo(
        model_name=artifact["model_name"],
        version=artifact["version"],
        algorithm_name=artifact["algorithm_name"],
        artifact_path=str(ARTIFACT_PATH),
        feature_columns=artifact["feature_columns"],
        metrics=artifact["metrics"],
        status="ready",
    )


@router.post("/predict/{organization_id}", response_model=RiskPredictionItem)
def predict_latest_organization_risk(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    snapshot = db.scalars(
        select(RiskFeatureSnapshot)
        .where(RiskFeatureSnapshot.organization_id == organization_id)
        .order_by(RiskFeatureSnapshot.period_date.desc())
        .limit(1)
    ).first()

    if snapshot is None:
        raise HTTPException(
            status_code=400,
            detail="No risk feature snapshot found for this organization",
        )

    return create_prediction_from_snapshot(
        db=db,
        organization=organization,
        snapshot=snapshot,
    )


@router.post("/predict-snapshot/{snapshot_id}", response_model=RiskPredictionItem)
def predict_risk_by_snapshot(
    snapshot_id: UUID,
    db: Session = Depends(get_db),
):
    snapshot = db.get(RiskFeatureSnapshot, snapshot_id)

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Feature snapshot not found")

    organization = db.get(Organization, snapshot.organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return create_prediction_from_snapshot(
        db=db,
        organization=organization,
        snapshot=snapshot,
    )


def create_prediction_from_snapshot(
    db: Session,
    organization: Organization,
    snapshot: RiskFeatureSnapshot,
) -> RiskPrediction:
    try:
        risk_score, risk_level, explanation = predict_risk(snapshot)
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error))

    model_name = explanation.get("model_name", "gradient_boosting_risk_model")
    model_version = explanation.get("version", "unknown")
    algorithm_name = explanation.get(
        "algorithm",
        "GradientBoostingClassifier + IsotonicCalibration",
    )

    model = db.scalar(
        select(MLModel)
        .where(MLModel.name == model_name)
        .where(MLModel.version == model_version)
    )

    if model is None:
        model = MLModel(
            name=model_name,
            version=model_version,
            algorithm_name=algorithm_name,
            target_name="default_risk",
            artifact_path="artifacts/risk_model.joblib",
            metrics=explanation.get("metrics"),
            parameters={
                "features": list(explanation["features"].keys()),
                "thresholds": {
                    "low": "< 0.25",
                    "medium": "0.25 - 0.55",
                    "high": "0.55 - 0.80",
                    "critical": ">= 0.80",
                },
            },
            trained_at=datetime.now(timezone.utc),
        )
        db.add(model)
        db.flush()

    prediction = RiskPrediction(
        organization_id=organization.id,
        feature_snapshot_id=snapshot.id,
        model_id=model.id,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation,
        recommendations={
            "actions": build_recommendations(risk_level.value)
        },
    )

    db.add(prediction)
    db.flush()

    create_audit_log(
        db=db,
        action="risk_prediction.created",
        entity_type="risk_prediction",
        entity_id=prediction.id,
        details={
            "organization_id": str(organization.id),
            "feature_snapshot_id": str(snapshot.id),
            "period_date": snapshot.period_date.isoformat(),
            "risk_score": str(risk_score),
            "risk_level": risk_level.value,
            "model": "gradient_boosting_risk_model",
        },
    )

    db.commit()
    db.refresh(prediction)

    return prediction


def build_recommendations(risk_level: str) -> list[str]:
    if risk_level == "low":
        return [
            "продолжить стандартное обслуживание клиента",
            "периодически обновлять финансовые показатели",
        ]

    if risk_level == "medium":
        return [
            "провести дополнительную проверку задолженности",
            "уточнить актуальность финансовой отчетности",
            "усилить мониторинг платежной дисциплины",
        ]

    if risk_level == "high":
        return [
            "ограничить кредитный лимит",
            "запросить дополнительные документы",
            "провести углубленный анализ просрочек и спорных ситуаций",
        ]

    return [
        "приостановить рискованные сделки",
        "передать организацию на рассмотрение ответственному аналитику",
        "провести комплексную проверку финансового состояния",
    ]
