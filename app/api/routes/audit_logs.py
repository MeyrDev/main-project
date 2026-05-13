"""
API для просмотра журнала аудита.

Позволяет получить список действий, выполненных в системе:
создание организаций, сделок, прогнозов, отчётов и других сущностей.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import AuditLog
from app.schemas import AuditLogItem

router = APIRouter(prefix="/audit-logs", tags=["Audit logs"])


@router.get("", response_model=list[AuditLogItem])
def get_audit_logs(
    db: Session = Depends(get_db),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(AuditLog)

    if action is not None:
        stmt = stmt.where(AuditLog.action == action)

    if entity_type is not None:
        stmt = stmt.where(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)

    stmt = (
        stmt.order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(stmt).all()