from uuid import UUID

from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str | None
    is_active: bool
