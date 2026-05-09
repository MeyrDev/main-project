from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Organization, RiskPrediction
from app.schemas import (
    OrganizationCreate,
    OrganizationDetail,
    OrganizationListItem,
    OrganizationRiskResponse,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=list[OrganizationListItem])
def get_organizations(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = (
        select(Organization)
        .order_by(Organization.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(stmt).all()


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
    db.commit()
    db.refresh(organization)

    return organization


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