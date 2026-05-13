"""
Сервис аудита действий.

Функции из этого файла создают записи в таблице audit_logs.
Аудит нужен, чтобы фиксировать важные действия пользователей:
создание организаций, запуск прогнозирования, изменение сделок и отчётов.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    user_id: UUID | None = None,
    details: dict | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )

    db.add(audit_log)
    db.flush()

    return audit_log