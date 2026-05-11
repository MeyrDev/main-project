"""
Модуль применения ML-модели.

Загружает сохранённый artifact, преобразует feature_snapshot в набор признаков,
рассчитывает вероятность риска и определяет категорию риска.
"""
from decimal import Decimal
from pathlib import Path

import joblib
import pandas as pd

from app.models import RiskFeatureSnapshot, RiskLevel


ARTIFACT_PATH = Path("artifacts/risk_model.joblib")


def load_artifact() -> dict:
    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            "ML model artifact not found. Run: python -m app.ml.train_model"
        )

    return joblib.load(ARTIFACT_PATH)


def snapshot_to_features(snapshot: RiskFeatureSnapshot) -> pd.DataFrame:
    revenue = float(snapshot.revenue or 0)
    debt_amount = float(snapshot.debt_amount or 0)

    debt_ratio = debt_amount / revenue if revenue > 0 else 1.0

    return pd.DataFrame(
        [
            {
                "revenue": revenue,
                "debt_amount": debt_amount,
                "debt_ratio": debt_ratio,
                "overdue_days_30": snapshot.overdue_days_30,
                "overdue_days_90": snapshot.overdue_days_90,
                "disputes_count": snapshot.disputes_count,
                "transactions_count": snapshot.transactions_count,
                "employees_count": snapshot.employees_count or 0,
            }
        ]
    )


def define_risk_level(score: Decimal) -> RiskLevel:
    value = float(score)

    if value < 0.25:
        return RiskLevel.low

    if value < 0.55:
        return RiskLevel.medium

    if value < 0.80:
        return RiskLevel.high

    return RiskLevel.critical


def predict_risk(snapshot: RiskFeatureSnapshot) -> tuple[Decimal, RiskLevel, dict]:
    artifact = load_artifact()

    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    features = snapshot_to_features(snapshot)
    features = features[feature_columns]

    probability = float(model.predict_proba(features)[0][1])

    risk_score = Decimal(str(round(probability, 5)))
    risk_level = define_risk_level(risk_score)

    explanation = {
        "method": "machine_learning_model",
        "model_name": artifact["model_name"],
        "version": artifact["version"],
        "algorithm": artifact["algorithm_name"],
        "metrics": artifact["metrics"],
        "features": {
            "revenue": str(snapshot.revenue),
            "debt_amount": str(snapshot.debt_amount),
            "debt_ratio": round(
                float(snapshot.debt_amount or 0) / float(snapshot.revenue or 1),
                4,
            ),
            "overdue_days_30": snapshot.overdue_days_30,
            "overdue_days_90": snapshot.overdue_days_90,
            "disputes_count": snapshot.disputes_count,
            "transactions_count": snapshot.transactions_count,
            "employees_count": snapshot.employees_count,
        },
    }

    return risk_score, risk_level, explanation