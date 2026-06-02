"""
Главный маршрутизатор API.

Подключает все группы endpoint'ов:
организации, признаки риска, прогнозы, dashboard и ML-модуль.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user

from app.api.routes import (
    auth_router,
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

protected = [Depends(get_current_user)]

api_router.include_router(auth_router)
api_router.include_router(organizations_router, dependencies=protected)
api_router.include_router(risk_predictions_router, dependencies=protected)
api_router.include_router(dashboard_router, dependencies=protected)
api_router.include_router(ml_router, dependencies=protected)
api_router.include_router(feature_snapshots_router, dependencies=protected)
api_router.include_router(deals_router, dependencies=protected)
api_router.include_router(interactions_router, dependencies=protected)
api_router.include_router(reports_router, dependencies=protected)
api_router.include_router(audit_logs_router, dependencies=protected)
