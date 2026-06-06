from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.report import ReportStatus, ReportType

class ReportCreate(BaseModel):
    organization_id: UUID | None = Field(
        default=None,
        description="Организация, по которой формируется отчёт",
    )

    created_by_id: UUID | None = Field(
        default=None,
        description="Пользователь, создавший отчёт",
    )

    title: str = Field(
        min_length=2,
        max_length=255,
        description="Название отчёта",
    )

    report_type: ReportType = Field(
        description="Тип отчёта",
    )

    parameters: dict | None = Field(
        default=None,
        description="Параметры формирования отчёта",
    )


class ReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID | None
    created_by_id: UUID | None

    title: str
    report_type: ReportType
    status: ReportStatus

    parameters: dict | None
    file_path: str | None

    created_at: datetime

class ReportData(BaseModel):
    id: UUID
    title: str
    report_type: ReportType
    status: ReportStatus
    generated_at: datetime
    parameters: dict | None
    content: dict