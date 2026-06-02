from decimal import Decimal
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from app.models import RiskFeatureSnapshot, RiskLevel

ARTIFACT_PATH = Path("artifacts/risk_model.joblib")


def load_artifact() -> dict:
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            "ML model artifact not found. Run: python -m app.ml.train_model"
        )

    artifact = joblib.load(ARTIFACT_PATH)

    if isinstance(artifact, dict):
        artifact.setdefault("model_name", "gradient_boosting_risk_model")
        artifact.setdefault("version", artifact.get("model_version", "unknown"))
        artifact.setdefault("algorithm_name", artifact.get("algorithm", "unknown"))
        artifact.setdefault("metrics", {})
        return artifact

    return {
        "model": artifact,
        "feature_columns": [
            "log_revenue",
            "log_debt_amount",
            "debt_ratio",
            "overdue_days_30",
            "overdue_days_90",
            "disputes_count",
            "transactions_count",
            "employees_count",
            "low_transactions_flag",
        ],
        "target_column": "target",
        "train_medians": {},
        "metrics": {},
        "model_name": "gradient_boosting_risk_model",
        "version": "legacy",
        "algorithm_name": artifact.__class__.__name__,
    }


def snapshot_to_features(snapshot: RiskFeatureSnapshot) -> pd.DataFrame:
    revenue = float(snapshot.revenue or 0)
    debt_amount = float(snapshot.debt_amount or 0)

    debt_ratio = debt_amount / revenue if revenue > 0 else 1.0
    low_transactions_flag = 1 if snapshot.transactions_count < 50 else 0

    return pd.DataFrame(
        [
            {
                "log_revenue": float(np.log1p(revenue)),
                "log_debt_amount": float(np.log1p(debt_amount)),
                "debt_ratio": debt_ratio,
                "overdue_days_30": snapshot.overdue_days_30,
                "overdue_days_90": snapshot.overdue_days_90,
                "disputes_count": snapshot.disputes_count,
                "transactions_count": snapshot.transactions_count,
                "employees_count": snapshot.employees_count or 0,
                "low_transactions_flag": low_transactions_flag,
            }
        ]
    )


def calculate_domain_score(snapshot: RiskFeatureSnapshot) -> Decimal:
    revenue = float(snapshot.revenue or 0)
    debt_amount = float(snapshot.debt_amount or 0)

    debt_ratio = debt_amount / revenue if revenue > 0 else 1.0

    score = 0.0
    score += min(debt_ratio, 1.0) * 0.38
    score += min(snapshot.overdue_days_30 / 60, 1.0) * 0.18
    score += min(snapshot.overdue_days_90 / 90, 1.0) * 0.22
    score += min(snapshot.disputes_count / 10, 1.0) * 0.14

    if snapshot.transactions_count < 50:
        score += 0.08

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


def build_main_factors(snapshot: RiskFeatureSnapshot) -> list[dict]:
    revenue = float(snapshot.revenue or 0)
    debt_amount = float(snapshot.debt_amount or 0)
    debt_ratio = debt_amount / revenue if revenue > 0 else 1.0

    factors = []

    if debt_ratio >= 0.4:
        factors.append(
            {
                "factor": "debt_ratio",
                "value": round(debt_ratio, 4),
                "impact": "high",
                "description": "Высокая доля задолженности относительно выручки",
            }
        )
    elif debt_ratio >= 0.2:
        factors.append(
            {
                "factor": "debt_ratio",
                "value": round(debt_ratio, 4),
                "impact": "medium",
                "description": "Умеренная долговая нагрузка организации",
            }
        )
    else:
        factors.append(
            {
                "factor": "debt_ratio",
                "value": round(debt_ratio, 4),
                "impact": "low",
                "description": "Низкая доля задолженности относительно выручки",
            }
        )

    if snapshot.overdue_days_90 > 0:
        factors.append(
            {
                "factor": "overdue_days_90",
                "value": snapshot.overdue_days_90,
                "impact": "high",
                "description": "Есть просрочка в 90-дневном окне",
            }
        )

    if snapshot.overdue_days_30 > 0:
        factors.append(
            {
                "factor": "overdue_days_30",
                "value": snapshot.overdue_days_30,
                "impact": "medium",
                "description": "Есть просрочка в 30-дневном окне",
            }
        )

    if snapshot.disputes_count > 0:
        factors.append(
            {
                "factor": "disputes_count",
                "value": snapshot.disputes_count,
                "impact": "medium",
                "description": "Зафиксированы спорные ситуации",
            }
        )

    if snapshot.transactions_count < 50:
        factors.append(
            {
                "factor": "transactions_count",
                "value": snapshot.transactions_count,
                "impact": "medium",
                "description": "Низкое количество транзакций за период",
            }
        )

    return factors


def predict_risk(snapshot: RiskFeatureSnapshot) -> tuple[Decimal, RiskLevel, dict]:
    artifact = load_artifact()

    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    features = snapshot_to_features(snapshot)
    features = features[feature_columns]

    train_medians = artifact.get("train_medians") or {}

    if train_medians:
        features = features.fillna(train_medians)

    model_probability = Decimal(str(round(float(model.predict_proba(features)[0][1]), 5)))
    domain_score = calculate_domain_score(snapshot)

    final_score = (model_probability * Decimal("0.7")) + (
        domain_score * Decimal("0.3")
    )
    final_score = Decimal(str(round(float(final_score), 5)))

    risk_level = define_risk_level(final_score)

    revenue = float(snapshot.revenue or 0)
    debt_amount = float(snapshot.debt_amount or 0)
    debt_ratio = debt_amount / revenue if revenue > 0 else 1.0

    explanation = {
        "method": "machine_learning_model_with_domain_calibration",
        "model_name": artifact["model_name"],
        "version": artifact["version"],
        "algorithm": artifact["algorithm_name"],
        "metrics": artifact["metrics"],
        "scores": {
            "model_probability": str(model_probability),
            "domain_score": str(domain_score),
            "final_score": str(final_score),
        },
        "features": {
            "revenue": str(snapshot.revenue),
            "debt_amount": str(snapshot.debt_amount),
            "debt_ratio": round(debt_ratio, 4),
            "overdue_days_30": snapshot.overdue_days_30,
            "overdue_days_90": snapshot.overdue_days_90,
            "disputes_count": snapshot.disputes_count,
            "transactions_count": snapshot.transactions_count,
            "employees_count": snapshot.employees_count,
        },
        "main_factors": build_main_factors(snapshot),
    }

    return final_score, risk_level, explanation
