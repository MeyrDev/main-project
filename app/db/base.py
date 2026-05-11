"""
Базовый класс SQLAlchemy ORM.

Все модели базы данных наследуются от Base.
Alembic использует Base.metadata для генерации и применения миграций.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
