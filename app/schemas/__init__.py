"""
Импорт Pydantic-схем.

Позволяет импортировать схемы из app.schemas единым способом.
""" 
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationDetail,
    OrganizationListItem,
    OrganizationFilters,
    OrganizationUpdate,
    OrganizationListResponse,
)
from app.schemas.risk_prediction import (
    OrganizationRiskHistoryItem,
    OrganizationRiskResponse,
    RiskPredictionItem,
)
from app.schemas.pagination import PaginatedResponse
from app.schemas.feature_snapshot import RiskFeatureSnapshotCreate, RiskFeatureSnapshotItem
from app.schemas.ml import MLModelInfo
from app.schemas.deal import DealCreate, DealItem, DealUpdate
from app.schemas.interaction import InteractionCreate, InteractionItem, InteractionUpdate
from app.schemas.report import ReportCreate, ReportData, ReportItem
from app.schemas.audit_log import AuditLogItem
from app.schemas.auth import CurrentUserResponse
from app.schemas.dashboard import (
    DashboardHighRiskOrganization,
    DashboardRecentAuditLog,
    DashboardRecentPrediction,
    DashboardSummary,
    RiskLevelCount,
)

__all__ = [
    "DashboardSummary",
    "OrganizationCreate",
    "OrganizationDetail",
    "OrganizationListItem",
    "OrganizationRiskResponse",
    "RiskLevelCount",
    "RiskPredictionItem",
    "RiskFeatureSnapshotCreate",
    "RiskFeatureSnapshotItem",
    "MLModelInfo",
    "OrganizationRiskHistoryItem",
    "OrganizationUpdate",
    "DealCreate",
    "DealUpdate",
    "DealItem",
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionItem",
    "ReportCreate",
    "ReportItem",
    "ReportData",
    "AuditLogItem",
    "CurrentUserResponse",
    "DashboardHighRiskOrganization",
    "DashboardRecentAuditLog",
    "DashboardRecentPrediction",
    "OrganizationFilters",
    "OrganizationListResponse",
    "PaginatedResponse",
]
