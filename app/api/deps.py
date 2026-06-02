"""
Зависимости FastAPI.

Содержит функцию get_db, которая создаёт и закрывает сессию базы данных
для каждого HTTP-запроса.
"""
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.session import SessionLocal
from app.models import User


security = HTTPBasic()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
) -> User:
    user = db.scalar(select(User).where(User.email == credentials.username))

    if (
        user is None
        or not user.is_active
        or not user.password_hash
        or not verify_password(credentials.password, user.password_hash)
    ):
        raise unauthorized_exception()

    return user
