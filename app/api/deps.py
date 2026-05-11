"""
Зависимости FastAPI.

Содержит функцию get_db, которая создаёт и закрывает сессию базы данных
для каждого HTTP-запроса.
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()