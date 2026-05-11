"""
Импорт всех ORM-моделей проекта.

Файл нужен, чтобы Alembic видел все модели через Base.metadata
и мог корректно создавать миграции.
"""
from app.models.audit_log import AuditLog
from app.models.data_import_batch import DataImportBatch, ImportStatus
from app.models.deal import Deal, DealStage
from app.models.external_data_source import DataSourceType, ExternalDataSource
from app.models.feature_snapshot import RiskFeatureSnapshot
from app.models.interaction import Interaction, InteractionType
from app.models.ml_model import MLModel
from app.models.organization import Organization
from app.models.organization_contact import OrganizationContact
from app.models.report import Report, ReportStatus, ReportType
from app.models.risk_prediction import RiskLevel, RiskPrediction
from app.models.role import Role
from app.models.user import User

__all__ = [
    "AuditLog",
    "DataImportBatch",
    "DataSourceType",
    "Deal",
    "DealStage",
    "ExternalDataSource",
    "ImportStatus",
    "Interaction",
    "InteractionType",
    "MLModel",
    "Organization",
    "OrganizationContact",
    "Report",
    "ReportStatus",
    "ReportType",
    "RiskFeatureSnapshot",
    "RiskLevel",
    "RiskPrediction",
    "Role",
    "User",
]