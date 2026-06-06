import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.ml.predictor import ARTIFACT_PATH, load_artifact, predict_risk
from app.ml.train_model import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    VALIDATION_DATASET_PATH,
    calculate_metrics,
    validate_dataset_file,
    validate_non_empty_columns,
    validate_target,
)
from app.models import (
    MLModel,
    Organization,
    RiskFeatureSnapshot,
    RiskPrediction,
)
from app.schemas import (
    MLModelInfo,
    MLTrainingReport,
    MLValidationEvaluation,
    RiskPredictionItem,
)
from app.services.audit import create_audit_log

router = APIRouter(prefix="/ml", tags=["ML"])

TRAINING_REPORT_JSON_PATH = Path("artifacts/training_report.json")
LATEST_VALIDATION_EVALUATION_PATH = Path("artifacts/latest_validation_evaluation.json")

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


@router.get("/training-report", response_model=MLTrainingReport)
def get_training_report():
    artifact_metadata = get_artifact_metadata(ARTIFACT_PATH)

    if not TRAINING_REPORT_JSON_PATH.exists():
        return MLTrainingReport(
            trained=False,
            artifact_path=str(ARTIFACT_PATH),
            **artifact_metadata,
            message=(
                "ML training report not found. Run: "
                "python -m app.ml.train_model"
            ),
        )

    try:
        report = json.loads(TRAINING_REPORT_JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"ML training report is not valid JSON: {error}",
        )

    payload = {
        key: report.get(key)
        for key in [
            "project_name",
            "model_version",
            "algorithm",
            "trained_at",
            "train_dataset_path",
            "validation_dataset_path",
            "train_rows",
            "validation_rows",
            "feature_columns",
            "target_column",
            "train_target_distribution",
            "validation_target_distribution",
            "metrics",
            "confusion_matrix",
            "artifact_path",
            "notes",
        ]
    }
    payload["trained"] = True
    payload.update(artifact_metadata)

    return MLTrainingReport(**payload)


@router.post("/evaluate-validation", response_model=MLValidationEvaluation)
def evaluate_validation_dataset():
    if not ARTIFACT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="ML model artifact not found. Run: python -m app.ml.train_model",
        )

    try:
        artifact = load_artifact()
        validation_df = load_validation_dataset_for_artifact(artifact)
        feature_columns = artifact.get("feature_columns") or FEATURE_COLUMNS
        target_column = artifact.get("target_column") or TARGET_COLUMN

        X_validation = prepare_validation_features(validation_df, artifact)
        y_validation = validation_df[target_column]
        model = artifact["model"]
        probabilities = pd.Series(
            model.predict_proba(X_validation)[:, 1],
            index=X_validation.index,
        )
        threshold = float(artifact.get("classification_threshold", 0.5))
        predictions = pd.Series(
            (probabilities >= threshold).astype(int),
            index=X_validation.index,
        )
        metrics, matrix = calculate_metrics(y_validation, probabilities, predictions)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(
            status_code=500,
            detail=f"ML model artifact is missing required key: {error}",
        )

    evaluated_at = datetime.now(timezone.utc).isoformat()
    artifact_metadata = get_artifact_metadata(ARTIFACT_PATH)
    result = {
        "evaluated": True,
        "evaluated_at": evaluated_at,
        "validation_dataset_path": str(VALIDATION_DATASET_PATH),
        "validation_rows": len(validation_df),
        "feature_columns": feature_columns,
        "target_column": target_column,
        "metrics": metrics,
        "confusion_matrix": {
            "labels": [0, 1],
            "matrix": matrix,
        },
        "artifact_path": str(ARTIFACT_PATH),
        "evaluation_path": str(LATEST_VALIDATION_EVALUATION_PATH),
        "notes": (
            "Validation evaluation loads the saved model artifact and applies it "
            "to validation_dataset.csv without retraining."
        ),
        **artifact_metadata,
    }

    LATEST_VALIDATION_EVALUATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_VALIDATION_EVALUATION_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return MLValidationEvaluation(**result)


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


def get_artifact_metadata(path: Path) -> dict:
    if not path.exists():
        return {
            "artifact_exists": False,
            "artifact_size_bytes": None,
            "artifact_modified_at": None,
        }

    stat = path.stat()

    return {
        "artifact_exists": True,
        "artifact_size_bytes": stat.st_size,
        "artifact_modified_at": datetime.fromtimestamp(
            stat.st_mtime,
            tz=timezone.utc,
        ).isoformat(),
    }


def load_validation_dataset_for_artifact(artifact: dict) -> pd.DataFrame:
    validate_dataset_file(VALIDATION_DATASET_PATH)

    feature_columns = artifact.get("feature_columns") or FEATURE_COLUMNS
    target_column = artifact.get("target_column") or TARGET_COLUMN
    required_columns = feature_columns + [target_column]

    validation_df = pd.read_csv(VALIDATION_DATASET_PATH)
    missing_columns = [
        column for column in required_columns if column not in validation_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset {VALIDATION_DATASET_PATH} is missing required columns: "
            f"{', '.join(missing_columns)}"
        )

    validation_df = validation_df[required_columns].copy()
    validate_target(validation_df, VALIDATION_DATASET_PATH)
    validate_non_empty_columns(validation_df, VALIDATION_DATASET_PATH)

    return validation_df


def prepare_validation_features(
    validation_df: pd.DataFrame,
    artifact: dict,
) -> pd.DataFrame:
    feature_columns = artifact.get("feature_columns") or FEATURE_COLUMNS
    X_validation = validation_df[feature_columns].copy()

    for column in feature_columns:
        X_validation[column] = pd.to_numeric(X_validation[column], errors="coerce")

    train_medians = artifact.get("train_medians") or {}
    if train_medians:
        X_validation = X_validation.fillna(train_medians)
    else:
        X_validation = X_validation.fillna(X_validation.median(numeric_only=True))

    missing_columns = [
        column for column in feature_columns if X_validation[column].isna().any()
    ]

    if missing_columns:
        raise ValueError(
            "Validation dataset contains empty values that could not be filled: "
            f"{', '.join(missing_columns)}"
        )

    return X_validation


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
