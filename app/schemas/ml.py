from pydantic import BaseModel


class MLModelInfo(BaseModel):
    model_name: str
    version: str
    algorithm_name: str
    artifact_path: str
    feature_columns: list[str]
    metrics: dict
    status: str