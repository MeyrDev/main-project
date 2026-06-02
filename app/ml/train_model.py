from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


PROJECT_NAME = "risk-crm-starter"
MODEL_NAME = "gradient_boosting_risk_model"
MODEL_VERSION = "1.2.0"
ALGORITHM_NAME = "GradientBoostingClassifier + IsotonicCalibration"

TRAIN_DATASET_PATH = Path("data/train_dataset.csv")
VALIDATION_DATASET_PATH = Path("data/validation_dataset.csv")
ARTIFACT_PATH = Path("artifacts/risk_model.joblib")
TRAINING_REPORT_JSON_PATH = Path("artifacts/training_report.json")
TRAINING_REPORT_MD_PATH = Path("artifacts/training_report.md")
VALIDATION_PREDICTIONS_PATH = Path("artifacts/validation_predictions.csv")

TARGET_COLUMN = "target"

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


def validate_dataset_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {path}. "
            "Run: python -m app.ml.prepare_datasets_from_csv"
        )


def validate_columns(df: pd.DataFrame, path: Path) -> None:
    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Dataset {path} is missing required columns: "
            f"{', '.join(missing_columns)}"
        )


def validate_target(df: pd.DataFrame, path: Path) -> None:
    df[TARGET_COLUMN] = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

    if df[TARGET_COLUMN].isna().any():
        raise ValueError(f"Dataset {path} contains rows with empty target values.")

    invalid_targets = sorted(set(df[TARGET_COLUMN].unique()) - {0, 1, 0.0, 1.0})

    if invalid_targets:
        raise ValueError(
            f"Dataset {path} target must contain only 0 and 1. "
            f"Invalid values: {invalid_targets}"
        )

    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)
    classes = set(df[TARGET_COLUMN].unique().tolist())

    if classes != {0, 1}:
        raise ValueError(
            f"Dataset {path} must contain both target classes 0 and 1. "
            f"Found classes: {sorted(classes)}"
        )


def validate_non_empty_columns(df: pd.DataFrame, path: Path) -> None:
    empty_columns = [
        column
        for column in FEATURE_COLUMNS
        if pd.to_numeric(df[column], errors="coerce").isna().all()
    ]

    if empty_columns:
        raise ValueError(
            f"Dataset {path} contains fully empty feature columns: "
            f"{', '.join(empty_columns)}"
        )


def load_dataset(path: Path) -> pd.DataFrame:
    validate_dataset_file(path)

    df = pd.read_csv(path)
    validate_columns(df, path)

    df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()
    validate_target(df, path)
    validate_non_empty_columns(df, path)

    return df


def prepare_features(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, dict[str, float]]:
    train_features = train_df[FEATURE_COLUMNS].copy()
    validation_features = validation_df[FEATURE_COLUMNS].copy()

    for column in FEATURE_COLUMNS:
        train_features[column] = pd.to_numeric(train_features[column], errors="coerce")
        validation_features[column] = pd.to_numeric(
            validation_features[column],
            errors="coerce",
        )

    train_medians = train_features.median(numeric_only=True)

    missing_medians = [
        column
        for column in FEATURE_COLUMNS
        if pd.isna(train_medians.get(column))
    ]

    if missing_medians:
        raise ValueError(
            "Cannot calculate train medians for feature columns: "
            f"{', '.join(missing_medians)}"
        )

    train_features = train_features.fillna(train_medians)
    validation_features = validation_features.fillna(train_medians)

    return (
        train_features,
        validation_features,
        train_df[TARGET_COLUMN],
        validation_df[TARGET_COLUMN],
        {column: float(train_medians[column]) for column in FEATURE_COLUMNS},
    )


def validate_class_counts(y_train: pd.Series, y_validation: pd.Series) -> None:
    train_distribution = y_train.value_counts().sort_index()
    validation_distribution = y_validation.value_counts().sort_index()

    if train_distribution.min() < 3:
        raise ValueError(
            "Train dataset has too few rows in one target class for "
            "CalibratedClassifierCV(cv=3). "
            f"Train distribution: {train_distribution.to_dict()}"
        )

    if validation_distribution.min() < 1:
        raise ValueError(
            "Validation dataset must contain both classes. "
            f"Validation distribution: {validation_distribution.to_dict()}"
        )


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> CalibratedClassifierCV:
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

    return model


def calculate_metrics(
    y_validation: pd.Series,
    probabilities: pd.Series,
    predictions: pd.Series,
) -> tuple[dict[str, float], list[list[int]]]:
    matrix = confusion_matrix(y_validation, predictions, labels=[0, 1]).tolist()

    metrics = {
        "roc_auc": round(float(roc_auc_score(y_validation, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_validation, probabilities)), 4),
        "f1": round(float(f1_score(y_validation, predictions, zero_division=0)), 4),
        "precision": round(
            float(precision_score(y_validation, predictions, zero_division=0)),
            4,
        ),
        "recall": round(float(recall_score(y_validation, predictions, zero_division=0)), 4),
        "accuracy": round(float(accuracy_score(y_validation, predictions)), 4),
        "brier_score": round(float(brier_score_loss(y_validation, probabilities)), 4),
    }

    return metrics, matrix


def select_classification_threshold(
    y_train: pd.Series,
    train_probabilities: pd.Series,
) -> tuple[float, float]:
    candidate_thresholds = sorted(set(round(float(value), 6) for value in train_probabilities))
    best_threshold = 0.5
    best_f1 = -1.0

    for threshold in candidate_thresholds:
        predictions = (train_probabilities >= threshold).astype(int)
        score = float(f1_score(y_train, predictions, zero_division=0))

        if score > best_f1:
            best_f1 = score
            best_threshold = threshold

    return best_threshold, round(best_f1, 4)


def build_report(
    trained_at: str,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    train_medians: dict[str, float],
    metrics: dict[str, float],
    matrix: list[list[int]],
    classification_threshold: float,
    train_threshold_f1: float,
) -> dict:
    return {
        "project_name": PROJECT_NAME,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "algorithm": ALGORITHM_NAME,
        "algorithm_name": ALGORITHM_NAME,
        "trained_at": trained_at,
        "train_dataset_path": str(TRAIN_DATASET_PATH),
        "validation_dataset_path": str(VALIDATION_DATASET_PATH),
        "train_rows": len(train_df),
        "validation_rows": len(validation_df),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "train_target_distribution": train_df[TARGET_COLUMN]
        .value_counts()
        .sort_index()
        .to_dict(),
        "validation_target_distribution": validation_df[TARGET_COLUMN]
        .value_counts()
        .sort_index()
        .to_dict(),
        "train_medians": train_medians,
        "classification_threshold": classification_threshold,
        "train_threshold_f1": train_threshold_f1,
        "metrics": metrics,
        "confusion_matrix": {
            "labels": [0, 1],
            "matrix": matrix,
        },
        "artifact_path": str(ARTIFACT_PATH),
        "validation_predictions_path": str(VALIDATION_PREDICTIONS_PATH),
        "notes": (
            "Model was trained only on train_dataset.csv. Validation metrics "
            "were calculated only on validation_dataset.csv. Missing values in "
            "validation were filled with medians calculated from train dataset. "
            "The binary classification threshold was selected on train dataset."
        ),
    }


def save_training_report_json(report: dict) -> None:
    TRAINING_REPORT_JSON_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_training_report_md(report: dict) -> None:
    metrics = report["metrics"]
    matrix = report["confusion_matrix"]["matrix"]

    content = f"""# Отчет об обучении ML-модели риска

## Цель обучения модели

Цель обучения - построить модель прогнозирования риска хозяйствующего субъекта для CRM-системы. Модель оценивает вероятность рискованного состояния организации по финансово-операционным признакам и возвращает риск-оценку для дальнейшего использования в backend prediction endpoints.

## Использованные датасеты

- Обучающая выборка: `{report["train_dataset_path"]}`
- Валидационная выборка: `{report["validation_dataset_path"]}`
- Количество строк в train dataset: `{report["train_rows"]}`
- Количество строк в validation dataset: `{report["validation_rows"]}`
- Распределение target в train: `{report["train_target_distribution"]}`
- Распределение target в validation: `{report["validation_target_distribution"]}`

Модель обучалась на `train_dataset.csv`, а проверка качества выполнялась на отдельном `validation_dataset.csv`.

## Признаки модели

{chr(10).join(f"- `{column}`" for column in report["feature_columns"])}

Целевая колонка: `{report["target_column"]}`.

## Алгоритм обучения

Использован алгоритм `{report["algorithm"]}`. Пропуски в train dataset заполнялись медианами train dataset. Для validation dataset использовались те же медианы, рассчитанные только по train dataset, чтобы избежать data leakage.

## Результаты проверки на validation_dataset

- ROC AUC: `{metrics["roc_auc"]}`
- PR AUC: `{metrics["pr_auc"]}`
- F1: `{metrics["f1"]}`
- Precision: `{metrics["precision"]}`
- Recall: `{metrics["recall"]}`
- Accuracy: `{metrics["accuracy"]}`
- Brier score: `{metrics["brier_score"]}`
- Порог классификации, выбранный на train dataset: `{report["classification_threshold"]}`

## Матрица ошибок

Метки классов: `[0, 1]`

| Actual / Predicted | 0 | 1 |
| --- | ---: | ---: |
| 0 | {matrix[0][0]} | {matrix[0][1]} |
| 1 | {matrix[1][0]} | {matrix[1][1]} |

## Вывод

Модель обучена на отдельной обучающей выборке `train_dataset.csv`. Качество проверено на отдельной валидационной выборке `validation_dataset.csv`, которая не использовалась при обучении. Для подтверждения результата доступны сохраненный artifact модели, JSON-отчет, markdown-отчет и CSV с предсказаниями на validation dataset.
"""

    TRAINING_REPORT_MD_PATH.write_text(content, encoding="utf-8")


def save_validation_predictions(
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
    probabilities: pd.Series,
    predictions: pd.Series,
) -> None:
    result = X_validation.copy()
    result.insert(0, "risk_probability", probabilities)
    result.insert(0, "predicted_target", predictions)
    result.insert(0, "actual_target", y_validation.reset_index(drop=True))
    result.to_csv(VALIDATION_PREDICTIONS_PATH, index=False)


def save_artifact(
    model: CalibratedClassifierCV,
    train_medians: dict[str, float],
    metrics: dict[str, float],
    trained_at: str,
    classification_threshold: float,
) -> None:
    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "train_medians": train_medians,
        "classification_threshold": classification_threshold,
        "metrics": metrics,
        "model_name": MODEL_NAME,
        "version": MODEL_VERSION,
        "model_version": MODEL_VERSION,
        "algorithm": ALGORITHM_NAME,
        "algorithm_name": ALGORITHM_NAME,
        "trained_at": trained_at,
        "train_dataset_path": str(TRAIN_DATASET_PATH),
        "validation_dataset_path": str(VALIDATION_DATASET_PATH),
        "training_report_path": str(TRAINING_REPORT_JSON_PATH),
    }

    joblib.dump(artifact, ARTIFACT_PATH)


def main() -> None:
    train_df = load_dataset(TRAIN_DATASET_PATH)
    validation_df = load_dataset(VALIDATION_DATASET_PATH)

    print(f"Train dataset path: {TRAIN_DATASET_PATH}")
    print(f"Validation dataset path: {VALIDATION_DATASET_PATH}")
    print(f"Train rows: {len(train_df)}")
    print(f"Validation rows: {len(validation_df)}")
    print(
        "Train target distribution: "
        f"{train_df[TARGET_COLUMN].value_counts().sort_index().to_dict()}"
    )
    print(
        "Validation target distribution: "
        f"{validation_df[TARGET_COLUMN].value_counts().sort_index().to_dict()}"
    )

    X_train, X_validation, y_train, y_validation, train_medians = prepare_features(
        train_df,
        validation_df,
    )
    validate_class_counts(y_train, y_validation)

    model = train_model(X_train, y_train)

    train_probabilities = pd.Series(
        model.predict_proba(X_train)[:, 1],
        index=X_train.index,
    )
    classification_threshold, train_threshold_f1 = select_classification_threshold(
        y_train,
        train_probabilities,
    )

    probabilities = pd.Series(
        model.predict_proba(X_validation)[:, 1],
        index=X_validation.index,
    )
    predictions = pd.Series(
        (probabilities >= classification_threshold).astype(int),
        index=X_validation.index,
    )

    metrics, matrix = calculate_metrics(y_validation, probabilities, predictions)
    trained_at = datetime.now(timezone.utc).isoformat()

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(
        trained_at=trained_at,
        train_df=train_df,
        validation_df=validation_df,
        train_medians=train_medians,
        metrics=metrics,
        matrix=matrix,
        classification_threshold=classification_threshold,
        train_threshold_f1=train_threshold_f1,
    )

    save_artifact(
        model=model,
        train_medians=train_medians,
        metrics=metrics,
        trained_at=trained_at,
        classification_threshold=classification_threshold,
    )
    save_training_report_json(report)
    save_training_report_md(report)
    save_validation_predictions(
        X_validation=X_validation.reset_index(drop=True),
        y_validation=y_validation.reset_index(drop=True),
        probabilities=probabilities.reset_index(drop=True),
        predictions=predictions.reset_index(drop=True),
    )

    print("Model trained successfully.")
    print(f"Artifact saved to: {ARTIFACT_PATH}")
    print(f"JSON report saved to: {TRAINING_REPORT_JSON_PATH}")
    print(f"Markdown report saved to: {TRAINING_REPORT_MD_PATH}")
    print(f"Validation predictions saved to: {VALIDATION_PREDICTIONS_PATH}")
    print(f"Validation metrics: {metrics}")
    print(f"Classification threshold selected on train: {classification_threshold}")
    print(f"Confusion matrix labels [0, 1]: {matrix}")


if __name__ == "__main__":
    main()
