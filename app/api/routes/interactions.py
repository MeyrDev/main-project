"""
API для работы с взаимодействиями.

Содержит методы получения истории взаимодействий организации,
создания нового взаимодействия и изменения существующей записи.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Deal, Interaction, Organization, User
from app.schemas import InteractionCreate, InteractionItem, InteractionUpdate

router = APIRouter(tags=["Interactions"])


@router.get(
    "/organizations/{organization_id}/interactions",
    response_model=list[InteractionItem],
)
def get_organization_interactions(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    stmt = (
        select(Interaction)
        .where(Interaction.organization_id == organization_id)
        .order_by(Interaction.happened_at.desc())
    )

    return db.scalars(stmt).all()


@router.post(
    "/organizations/{organization_id}/interactions",
    response_model=InteractionItem,
    status_code=201,
)
def create_organization_interaction(
    organization_id: UUID,
    payload: InteractionCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    if payload.user_id is not None:
        user = db.get(User, payload.user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    if payload.deal_id is not None:
        deal = db.get(Deal, payload.deal_id)

        if deal is None:
            raise HTTPException(status_code=404, detail="Deal not found")

        if deal.organization_id != organization_id:
            raise HTTPException(
                status_code=400,
                detail="Deal does not belong to this organization",
            )

    interaction = Interaction(
        organization_id=organization_id,
        user_id=payload.user_id,
        deal_id=payload.deal_id,
        interaction_type=payload.interaction_type,
        subject=payload.subject,
        description=payload.description,
        happened_at=payload.happened_at,
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return interaction


@router.patch(
    "/interactions/{interaction_id}",
    response_model=InteractionItem,
)
def update_interaction(
    interaction_id: UUID,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
):
    interaction = db.get(Interaction, interaction_id)

    if interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        return interaction

    user_id = update_data.get("user_id")

    if user_id is not None:
        user = db.get(User, user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    deal_id = update_data.get("deal_id")

    if deal_id is not None:
        deal = db.get(Deal, deal_id)

        if deal is None:
            raise HTTPException(status_code=404, detail="Deal not found")

        if deal.organization_id != interaction.organization_id:
            raise HTTPException(
                status_code=400,
                detail="Deal does not belong to this organization",
            )

    for field_name, value in update_data.items():
        setattr(interaction, field_name, value)

    db.commit()
    db.refresh(interaction)

    return interaction