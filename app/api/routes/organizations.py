"""
API для работы с организациями.

Содержит методы получения списка организаций, просмотра карточки организации,
создания организации и получения последней оценки риска.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Organization, RiskPrediction, organization
from app.schemas import (
    OrganizationCreate,
    OrganizationDetail,
    OrganizationListItem,
    OrganizationFilters,
    OrganizationRiskResponse,
    OrganizationRiskHistoryItem,
    OrganizationUpdate,
    OrganizationListResponse,
)
from app.services.audit import create_audit_log

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.get("", response_model=OrganizationListResponse)
def get_organizations(
    db: Session = Depends(get_db),
    search: str | None = Query(
        default=None,
        description="Поиск по названию организации или БИН",
    ),
    industry: str | None = Query(
        default=None,
        description="Фильтр по отрасли",
    ),
    region: str | None = Query(
        default=None,
        description="Фильтр по региону",
    ),
    segment: str | None = Query(
        default=None,
        description="Фильтр по сегменту бизнеса",
    ),
    status: str | None = Query(
        default=None,
        description="Фильтр по статусу организации",
    ),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    base_stmt = select(Organization)

    if search:
        search_pattern = f"%{search.strip()}%"

        base_stmt = base_stmt.where(
            or_(
                Organization.name.ilike(search_pattern),
                Organization.bin.ilike(search_pattern),
            )
        )

    if industry:
        base_stmt = base_stmt.where(Organization.industry == industry)

    if region:
        base_stmt = base_stmt.where(Organization.region == region)

    if segment:
        base_stmt = base_stmt.where(Organization.segment == segment)

    if status:
        base_stmt = base_stmt.where(Organization.status == status)

    total_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = db.scalar(total_stmt) or 0

    items_stmt = (
        base_stmt
        .order_by(Organization.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    items = db.scalars(items_stmt).all()

    return OrganizationListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=OrganizationDetail, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
):
    if payload.bin:
        existing = db.scalar(
            select(Organization).where(Organization.bin == payload.bin)
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="Organization with this BIN already exists",
            )

    organization = Organization(**payload.model_dump())

    db.add(organization)
    db.flush()

    create_audit_log(
        db=db,
        action="organization.created",
        entity_type="organization",
        entity_id=organization.id,
        details={
            "name": organization.name,
            "bin": organization.bin,
            "industry": organization.industry,
            "region": organization.region,
        },
    )
    
    db.commit()
    db.refresh(organization)

    return organization

@router.get("/filters", response_model=OrganizationFilters)
def get_organization_filters(
    db: Session = Depends(get_db),
):
    industries = get_distinct_values(db, Organization.industry)
    regions = get_distinct_values(db, Organization.region)
    segments = get_distinct_values(db, Organization.segment)
    statuses = get_distinct_values(db, Organization.status)

    return OrganizationFilters(
        industries=industries,
        regions=regions,
        segments=segments,
        statuses=statuses,
    )


def get_distinct_values(db: Session, column) -> list[str]:
    stmt = (
        select(column)
        .where(column.is_not(None))
        .where(func.length(column) > 0)
        .distinct()
        .order_by(column)
    )

    return [value for value in db.scalars(stmt).all() if value]

@router.get("/{organization_id}", response_model=OrganizationDetail)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization


@router.get("/{organization_id}/risk", response_model=OrganizationRiskResponse)
def get_organization_risk(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    stmt = (
        select(RiskPrediction)
        .where(RiskPrediction.organization_id == organization_id)
        .order_by(RiskPrediction.predicted_at.desc())
        .limit(1)
    )

    prediction = db.scalars(stmt).first()

    return {
        "organization_id": organization.id,
        "organization_name": organization.name,
        "risk_prediction": prediction,
    }

@router.get("/{organization_id}/risk-history", response_model=list[OrganizationRiskHistoryItem])
def get_organization_risk_history(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    stmt = (
        select(RiskPrediction)
        .where(RiskPrediction.organization_id == organization_id)
        .order_by(RiskPrediction.predicted_at.desc())
    )

    return db.scalars(stmt).all()

@router.patch("/{organization_id}", response_model=OrganizationDetail)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        return organization

    new_bin = update_data.get("bin")

    if new_bin and new_bin != organization.bin:
        existing = db.scalar(
            select(Organization).where(Organization.bin == new_bin)
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="Organization with this BIN already exists",
            )

    for field_name, value in update_data.items():
        setattr(organization, field_name, value)

    create_audit_log(
        db=db,
        action="organization.updated",
        entity_type="organization",
        entity_id=organization.id,
        details={
            "updated_fields": list(update_data.keys()),
        },
    )

    db.commit()
    db.refresh(organization)

    return organization