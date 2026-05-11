"""
Настройка подключения к PostgreSQL.

engine отвечает за соединение с базой данных.
SessionLocal используется для создания сессий работы с БД в API-методах.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
