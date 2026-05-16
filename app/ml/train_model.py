"""
Скрипт обучения ML-модели риска.

Генерирует демонстрационный обучающий набор данных, формирует признаки,
обучает модель классификации риска, рассчитывает метрики качества
и сохраняет artifact в artifacts/risk_model.joblib.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


ARTIFACT_PATH = Path("artifacts/risk_model.joblib")

FEATURE_COLUMNS = [
    "log_revenue",
    "log_debt_amount",
    "debt_ratio",
    "overdue_days_30",
    "overdue_days_90",
    "disputes_count",
    "transactions_count",
    "employees_count",
    "low_transactions_flag",
]


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def generate_training_data(n_samples: int = 8000, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    revenue = rng.lognormal(mean=18.3, sigma=1.2, size=n_samples)
    employees_count = rng.integers(3, 700, size=n_samples)
    transactions_count = rng.integers(1, 800, size=n_samples)

    debt_ratio_base = rng.beta(a=1.8, b=4.5, size=n_samples)
    debt_amount = revenue * debt_ratio_base

    overdue_days_30 = rng.poisson(lam=7, size=n_samples)
    overdue_days_90 = rng.poisson(lam=2.5, size=n_samples)
    disputes_count = rng.poisson(lam=1.8, size=n_samples)

    debt_ratio = debt_amount / np.maximum(revenue, 1)
    low_transactions_flag = (transactions_count < 50).astype(int)

    log_revenue = np.log1p(revenue)
    log_debt_amount = np.log1p(debt_amount)

    domain_score = (
        np.clip(debt_ratio, 0, 1) * 0.38
        + np.clip(overdue_days_30 / 60, 0, 1) * 0.18
        + np.clip(overdue_days_90 / 90, 0, 1) * 0.22
        + np.clip(disputes_count / 10, 0, 1) * 0.14
        + low_transactions_flag * 0.08
    )

    noise = rng.normal(0, 0.08, size=n_samples)
    probability = np.clip(domain_score + noise, 0, 1)

    target = rng.binomial(1, probability)

    df = pd.DataFrame(
        {
            "revenue": revenue,
            "debt_amount": debt_amount,
            "log_revenue": log_revenue,
            "log_debt_amount": log_debt_amount,
            "debt_ratio": debt_ratio,
            "overdue_days_30": overdue_days_30,
            "overdue_days_90": overdue_days_90,
            "disputes_count": disputes_count,
            "transactions_count": transactions_count,
            "employees_count": employees_count,
            "low_transactions_flag": low_transactions_flag,
            "target": target,
        }
    )

    return df


def main() -> None:
    df = generate_training_data()

    X = df[FEATURE_COLUMNS]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    base_model = GradientBoostingClassifier(
        random_state=42,
        n_estimators=180,
        learning_rate=0.05,
        max_depth=3,
    )

    model = CalibratedClassifierCV(
        estimator=base_model,
        method="isotonic",
        cv=3,
    )

    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_test, probabilities)), 4),
        "f1": round(float(f1_score(y_test, predictions)), 4),
        "brier_score": round(float(brier_score_loss(y_test, probabilities)), 4),
    }

    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics,
        "model_name": "gradient_boosting_risk_model",
        "version": "1.1.0",
        "algorithm_name": "GradientBoostingClassifier + IsotonicCalibration",
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, ARTIFACT_PATH)

    print("Model trained successfully.")
    print(f"Artifact saved to: {ARTIFACT_PATH}")
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    main()