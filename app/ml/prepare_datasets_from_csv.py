from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


DEFAULT_INPUT_PATH = Path("data/raw/risk_dataset.csv")
TRAIN_OUTPUT_PATH = Path("data/train_dataset.csv")
VALIDATION_OUTPUT_PATH = Path("data/validation_dataset.csv")

TRAIN_SIZE = 500
VALIDATION_SIZE = 300
TOTAL_SIZE = TRAIN_SIZE + VALIDATION_SIZE
RANDOM_STATE = 42
LOW_TRANSACTIONS_THRESHOLD = 50

REQUIRED_COLUMNS = [
    "revenue",
    "debt_amount",
    "debt_ratio",
    "overdue_days_30",
    "overdue_days_90",
    "disputes_count",
    "transactions_count",
    "employees_count",
    "target",
]

DERIVED_COLUMNS = [
    "log_revenue",
    "log_debt_amount",
    "low_transactions_flag",
]

FINAL_COLUMNS = [
    "revenue",
    "debt_amount",
    "debt_ratio",
    "overdue_days_30",
    "overdue_days_90",
    "disputes_count",
    "transactions_count",
    "employees_count",
    "log_revenue",
    "log_debt_amount",
    "low_transactions_flag",
    "target",
]

NUMERIC_FEATURE_COLUMNS = [column for column in FINAL_COLUMNS if column != "target"]

BANKRUPTCY_TARGET_COLUMN = "Bankrupt?"

BANKRUPTCY_COLUMN_HINTS = {
    "revenue": [
        "Revenue Per Share",
        "Total income/Total expense",
        "Operating Gross Margin",
    ],
    "debt_ratio": [
        "Debt ratio %",
        "Liability to Equity",
        "Total debt/Total net worth",
    ],
    "overdue_days_30": [
        "Average Collection Days",
        "Accounts Receivable Turnover",
        "Current Liability to Current Assets",
    ],
    "overdue_days_90": [
        "No-credit Interval",
        "Current Liability to Assets",
        "Borrowing dependency",
    ],
    "disputes_count": [
        "Contingent liabilities/Net worth",
        "Liability-Assets Flag",
        "Interest Expense Ratio",
    ],
    "transactions_count": [
        "Total Asset Turnover",
        "Inventory Turnover Rate",
        "Current Asset Turnover Rate",
    ],
    "employees_count": [
        "Revenue per person",
        "Operating profit per person",
        "Allocation rate per person",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare train and validation ML datasets from a risk CSV file.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=f"Path to source CSV. Default: {DEFAULT_INPUT_PATH}",
    )
    parser.add_argument(
        "--train-output",
        type=Path,
        default=TRAIN_OUTPUT_PATH,
        help=f"Path to train dataset output. Default: {TRAIN_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--validation-output",
        type=Path,
        default=VALIDATION_OUTPUT_PATH,
        help=f"Path to validation dataset output. Default: {VALIDATION_OUTPUT_PATH}",
    )
    return parser.parse_args()


def find_input_csv(explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path

    if DEFAULT_INPUT_PATH.exists():
        return DEFAULT_INPUT_PATH

    csv_files = sorted(
        path
        for path in Path(".").glob("**/*.csv")
        if not any(part in {".venv", "node_modules", "__pycache__", "dist", "build"} for part in path.parts)
        and path not in {TRAIN_OUTPUT_PATH, VALIDATION_OUTPUT_PATH}
    )

    if len(csv_files) == 1:
        return csv_files[0]

    return DEFAULT_INPUT_PATH


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        raise ValueError(
            "Source CSV is missing required columns: "
            f"{', '.join(missing_columns)}"
        )


def find_column_by_hints(df: pd.DataFrame, hints: list[str]) -> str | None:
    normalized_columns = {
        column.lower().strip(): column
        for column in df.columns
    }

    for hint in hints:
        normalized_hint = hint.lower()

        for normalized_column, original_column in normalized_columns.items():
            if normalized_hint in normalized_column:
                return original_column

    return None


def numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce")


def fill_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    median_value = series.median()

    if pd.isna(median_value):
        median_value = default

    return series.fillna(median_value)


def normalize_to_range(series: pd.Series, minimum: float, maximum: float) -> pd.Series:
    series = fill_numeric(series)
    lower = series.quantile(0.01)
    upper = series.quantile(0.99)

    if pd.isna(lower) or pd.isna(upper) or lower == upper:
        return pd.Series(np.full(len(series), minimum), index=series.index)

    normalized = (series.clip(lower, upper) - lower) / (upper - lower)
    return normalized * (maximum - minimum) + minimum


def looks_like_bankruptcy_csv(df: pd.DataFrame) -> bool:
    return BANKRUPTCY_TARGET_COLUMN in df.columns


def build_crm_dataset_from_bankruptcy_csv(df: pd.DataFrame) -> pd.DataFrame:
    columns = {
        target_column: find_column_by_hints(df, hints)
        for target_column, hints in BANKRUPTCY_COLUMN_HINTS.items()
    }

    missing_source_columns = [
        target_column
        for target_column, source_column in columns.items()
        if source_column is None
    ]

    if missing_source_columns:
        raise ValueError(
            "Source CSV looks like a bankruptcy dataset, but some columns "
            "needed for CRM feature conversion were not found: "
            f"{', '.join(missing_source_columns)}."
        )

    converted = pd.DataFrame(index=df.index)

    raw_revenue = fill_numeric(numeric_series(df, columns["revenue"]), default=1.0)
    raw_revenue = raw_revenue.clip(lower=0)
    revenue_scale = 1_000_000 if raw_revenue.max() <= 10_000 else 1
    converted["revenue"] = raw_revenue * revenue_scale

    raw_debt_ratio = fill_numeric(numeric_series(df, columns["debt_ratio"]))
    converted["debt_ratio"] = raw_debt_ratio.clip(lower=0, upper=1)
    converted["debt_amount"] = converted["revenue"] * converted["debt_ratio"]

    converted["overdue_days_30"] = normalize_to_range(
        numeric_series(df, columns["overdue_days_30"]),
        minimum=0,
        maximum=60,
    ).round()
    converted["overdue_days_90"] = normalize_to_range(
        numeric_series(df, columns["overdue_days_90"]),
        minimum=0,
        maximum=120,
    ).round()
    converted["disputes_count"] = normalize_to_range(
        numeric_series(df, columns["disputes_count"]),
        minimum=0,
        maximum=12,
    ).round()
    converted["transactions_count"] = normalize_to_range(
        numeric_series(df, columns["transactions_count"]),
        minimum=10,
        maximum=800,
    ).round()
    converted["employees_count"] = normalize_to_range(
        numeric_series(df, columns["employees_count"]),
        minimum=3,
        maximum=700,
    ).round()
    converted["target"] = numeric_series(df, BANKRUPTCY_TARGET_COLUMN)

    return converted


def normalize_source_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if all(column in df.columns for column in REQUIRED_COLUMNS):
        return df

    if looks_like_bankruptcy_csv(df):
        print(
            "Source CSV does not contain CRM columns. "
            "Detected bankruptcy dataset and converted it to CRM risk features."
        )
        return build_crm_dataset_from_bankruptcy_csv(df)

    validate_required_columns(df)
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    if "log_revenue" not in df.columns:
        df["log_revenue"] = np.log1p(df["revenue"].clip(lower=0))

    if "log_debt_amount" not in df.columns:
        df["log_debt_amount"] = np.log1p(df["debt_amount"].clip(lower=0))

    if "low_transactions_flag" not in df.columns:
        df["low_transactions_flag"] = (
            df["transactions_count"] < LOW_TRANSACTIONS_THRESHOLD
        ).astype(int)

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["target"] = pd.to_numeric(df["target"], errors="coerce")
    df = df.dropna(subset=["target"])

    for column in REQUIRED_COLUMNS:
        if column == "target":
            continue

        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = add_derived_columns(df)

    for column in DERIVED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    invalid_targets = sorted(set(df["target"].dropna().unique()) - {0, 1, 0.0, 1.0})

    if invalid_targets:
        raise ValueError(
            "Target column must contain only 0 and 1 after cleaning. "
            f"Invalid values found: {invalid_targets}"
        )

    df["target"] = df["target"].astype(int)

    for column in NUMERIC_FEATURE_COLUMNS:
        median_value = df[column].median()

        if pd.isna(median_value):
            raise ValueError(
                f"Column '{column}' contains no numeric values after conversion."
            )

        df[column] = df[column].fillna(median_value)

    df = df[FINAL_COLUMNS].drop_duplicates().reset_index(drop=True)

    return df


def validate_cleaned_dataset(df: pd.DataFrame) -> None:
    rows_count = len(df)

    if rows_count < TOTAL_SIZE:
        raise ValueError(
            f"Not enough rows after cleaning: found {rows_count}, "
            f"required at least {TOTAL_SIZE}."
        )

    class_counts = df["target"].value_counts().sort_index()
    classes = set(class_counts.index.tolist())

    if classes != {0, 1}:
        raise ValueError(
            "Target must contain both classes 0 and 1 after cleaning. "
            f"Found classes: {sorted(classes)}."
        )

    if class_counts.min() < 2:
        raise ValueError(
            "One of the target classes has too few rows for stratified splitting. "
            f"Class distribution: {class_counts.to_dict()}."
        )


def split_datasets(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        train_df, validation_df = train_test_split(
            df,
            train_size=TRAIN_SIZE,
            test_size=VALIDATION_SIZE,
            stratify=df["target"],
            random_state=RANDOM_STATE,
            shuffle=True,
        )
    except ValueError as error:
        class_counts = df["target"].value_counts().sort_index().to_dict()
        raise ValueError(
            "Cannot create stratified train/validation datasets. "
            f"Class distribution: {class_counts}. Details: {error}"
        ) from error

    train_classes = set(train_df["target"].unique().tolist())
    validation_classes = set(validation_df["target"].unique().tolist())

    if train_classes != {0, 1} or validation_classes != {0, 1}:
        raise ValueError(
            "One of the target classes is too rare for both output datasets "
            "to contain classes 0 and 1. "
            f"Train classes: {sorted(train_classes)}, "
            f"validation classes: {sorted(validation_classes)}."
        )

    return (
        train_df.sort_index().reset_index(drop=True),
        validation_df.sort_index().reset_index(drop=True),
    )


def print_report(
    input_path: Path,
    source_rows_count: int,
    cleaned_rows_count: int,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
) -> None:
    print("Datasets prepared successfully.")
    print(f"Source CSV: {input_path}")
    print(f"Rows in source file: {source_rows_count}")
    print(f"Rows after cleaning: {cleaned_rows_count}")
    print(f"Rows in train dataset: {len(train_df)}")
    print(f"Rows in validation dataset: {len(validation_df)}")
    print(f"Target distribution in train: {train_df['target'].value_counts().sort_index().to_dict()}")
    print(
        "Target distribution in validation: "
        f"{validation_df['target'].value_counts().sort_index().to_dict()}"
    )
    print(f"Final columns: {', '.join(FINAL_COLUMNS)}")


def main() -> None:
    args = parse_args()
    input_path = find_input_csv(args.input)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Source CSV not found: {input_path}. "
            f"Place your dataset at {DEFAULT_INPUT_PATH} or pass --input <path>."
        )

    df = pd.read_csv(input_path)
    source_rows_count = len(df)

    df = normalize_source_dataset(df)
    validate_required_columns(df)

    cleaned_df = clean_dataset(df)
    validate_cleaned_dataset(cleaned_df)

    train_df, validation_df = split_datasets(cleaned_df)

    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(args.train_output, index=False)
    validation_df.to_csv(args.validation_output, index=False)

    print_report(
        input_path=input_path,
        source_rows_count=source_rows_count,
        cleaned_rows_count=len(cleaned_df),
        train_df=train_df,
        validation_df=validation_df,
    )
    print(f"Train dataset saved to: {args.train_output}")
    print(f"Validation dataset saved to: {args.validation_output}")


if __name__ == "__main__":
    main()
