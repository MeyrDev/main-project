"""
Главный маршрутизатор API.

Подключает все группы endpoint'ов:
организации, признаки риска, прогнозы, dashboard и ML-модуль.
"""
from fastapi import APIRouter

from app.api.routes import (
    dashboard_router,
    ml_router,
    organizations_router,
    risk_predictions_router,
    feature_snapshots_router,
    deals_router,
    interactions_router,
    reports_router,
    audit_logs_router
)

api_router = APIRouter(prefix="/api")

api_router.include_router(organizations_router)
api_router.include_router(risk_predictions_router)
api_router.include_router(dashboard_router)
api_router.include_router(ml_router)
api_router.include_router(feature_snapshots_router)
api_router.include_router(deals_router)
api_router.include_router(interactions_router)
api_router.include_router(reports_router)
api_router.include_router(audit_logs_router)
