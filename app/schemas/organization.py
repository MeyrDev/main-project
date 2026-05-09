from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class OrganizationCreate(BaseModel):
    bin: str | None = None
    name: str
    industry: str | None = None
    region: str | None = None
    segment: str | None = None
    status: str = "active"
    annual_revenue: Decimal | None = None
    employees_count: int | None = None
    description: str | None = None


class OrganizationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bin: str | None
    name: str
    industry: str | None
    region: str | None
    segment: str | None
    status: str
    annual_revenue: Decimal | None
    employees_count: int | None


class OrganizationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bin: str | None
    name: str
    industry: str | None
    region: str | None
    segment: str | None
    status: str
    annual_revenue: Decimal | None
    employees_count: int | None
    description: str | None
    created_at: datetime
    updated_at: datetime