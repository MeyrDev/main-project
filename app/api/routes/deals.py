"""
API для работы со сделками.

Содержит методы получения сделок организации, создания новой сделки
и изменения существующей сделки.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Deal, Organization, User
from app.schemas import DealCreate, DealItem, DealUpdate

router = APIRouter(tags=["Deals"])


@router.get(
    "/organizations/{organization_id}/deals",
    response_model=list[DealItem],
)
def get_organization_deals(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    stmt = (
        select(Deal)
        .where(Deal.organization_id == organization_id)
        .order_by(Deal.created_at.desc())
    )

    return db.scalars(stmt).all()


@router.post(
    "/organizations/{organization_id}/deals",
    response_model=DealItem,
    status_code=201,
)
def create_organization_deal(
    organization_id: UUID,
    payload: DealCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    if payload.owner_id is not None:
        owner = db.get(User, payload.owner_id)

        if owner is None:
            raise HTTPException(status_code=404, detail="Owner user not found")

    deal = Deal(
        organization_id=organization_id,
        owner_id=payload.owner_id,
        title=payload.title,
        stage=payload.stage,
        amount=payload.amount,
        currency=payload.currency,
        expected_close_date=payload.expected_close_date,
        description=payload.description,
    )

    db.add(deal)
    db.commit()
    db.refresh(deal)

    return deal


@router.patch(
    "/deals/{deal_id}",
    response_model=DealItem,
)
def update_deal(
    deal_id: UUID,
    payload: DealUpdate,
    db: Session = Depends(get_db),
):
    deal = db.get(Deal, deal_id)

    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        return deal

    owner_id = update_data.get("owner_id")

    if owner_id is not None:
        owner = db.get(User, owner_id)

        if owner is None:
            raise HTTPException(status_code=404, detail="Owner user not found")

    for field_name, value in update_data.items():
        setattr(deal, field_name, value)

    db.commit()
    db.refresh(deal)

    return deal