"""
Точка входа FastAPI-приложения.

Файл создаёт экземпляр приложения, подключает все API-маршруты
и предоставляет health-check endpoint для проверки работоспособности backend.
"""

from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
    title="Risk CRM API",
    description="CRM-система прогнозирования рисков хозяйствующих субъектов",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "risk-crm-api",
    }