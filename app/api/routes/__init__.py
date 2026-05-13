"""
Импорт всех маршрутов API.

Файл нужен, чтобы общий api_router мог подключить все группы endpoint'ов.
"""
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.ml import router as ml_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.risk_predictions import router as risk_predictions_router
from app.api.routes.feature_snapshots import router as feature_snapshots_router
from app.api.routes.deals import router as deals_router
from app.api.routes.interactions import router as interactions_router
from app.api.routes.reports import router as reports_router

__all__ = [
    "dashboard_router",
    "ml_router",
    "organizations_router",
    "risk_predictions_router",
    "feature_snapshots_router",
    "deals_router",
    "interactions_router",
    "reports_router",
]