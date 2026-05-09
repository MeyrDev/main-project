from fastapi import APIRouter

from app.api.routes import (
    dashboard_router,
    ml_router,
    organizations_router,
    risk_predictions_router,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(organizations_router)
api_router.include_router(risk_predictions_router)
api_router.include_router(dashboard_router)
api_router.include_router(ml_router)