"""
Pydantic-схемы для взаимодействий.

Взаимодействия фиксируют историю коммуникаций с организацией:
звонки, письма, встречи, заметки и задачи.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.interaction import InteractionType


class InteractionCreate(BaseModel):
    user_id: UUID | None = Field(
        default=None,
        description="Пользователь, который создал взаимодействие",
    )

    deal_id: UUID | None = Field(
        default=None,
        description="Связанная сделка, если взаимодействие относится к сделке",
    )

    interaction_type: InteractionType = Field(
        description="Тип взаимодействия: call, email, meeting, note или task",
    )

    subject: str = Field(
        min_length=2,
        max_length=255,
        description="Тема взаимодействия",
    )

    description: str | None = Field(
        default=None,
        description="Описание взаимодействия",
    )

    happened_at: datetime = Field(
        description="Дата и время взаимодействия",
    )


class InteractionUpdate(BaseModel):
    user_id: UUID | None = None
    deal_id: UUID | None = None
    interaction_type: InteractionType | None = None
    subject: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    happened_at: datetime | None = None


class InteractionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID | None
    deal_id: UUID | None

    interaction_type: InteractionType
    subject: str
    description: str | None

    happened_at: datetime
    created_at: datetime