"""
Pydantic-схемы для журнала аудита.

Определяют формат ответа API при просмотре действий пользователей.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    details: dict | None
    created_at: datetime