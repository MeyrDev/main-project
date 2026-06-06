from typing import Any
from pydantic import BaseModel, Field


class MLModelInfo(BaseModel):
    model_name: str
    version: str
    algorithm_name: str
    artifact_path: str
    feature_columns: list[str]
    metrics: dict
    status: str


class MLTrainingReport(BaseModel):
    trained: bool
    project_name: str | None = None
    model_version: str | None = None
    algorithm: str | None = None
    trained_at: str | None = None
    train_dataset_path: str | None = None
    validation_dataset_path: str | None = None
    train_rows: int | None = None
    validation_rows: int | None = None
    feature_columns: list[str] = Field(default_factory=list)
    target_column: str | None = None
    train_target_distribution: dict[str, Any] = Field(default_factory=dict)
    validation_target_distribution: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    confusion_matrix: dict[str, Any] | list[list[int]] | None = None
    artifact_path: str | None = None
    notes: str | None = None
    artifact_exists: bool = False
    artifact_size_bytes: int | None = None
    artifact_modified_at: str | None = None
    message: str | None = None


class MLValidationEvaluation(BaseModel):
    evaluated: bool
    evaluated_at: str
    validation_dataset_path: str
    validation_rows: int
    feature_columns: list[str]
    target_column: str
    metrics: dict[str, float]
    confusion_matrix: dict[str, Any]
    artifact_path: str
    artifact_exists: bool
    artifact_size_bytes: int | None = None
    artifact_modified_at: str | None = None
    evaluation_path: str
    notes: str
