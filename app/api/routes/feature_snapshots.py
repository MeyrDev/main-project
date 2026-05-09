from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Organization, RiskFeatureSnapshot
from app.schemas import RiskFeatureSnapshotCreate, RiskFeatureSnapshotItem

router = APIRouter(
    prefix="/organizations/{organization_id}/feature-snapshots",
    tags=["Risk feature snapshots"],
)


@router.get("", response_model=list[RiskFeatureSnapshotItem])
def get_feature_snapshots(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    stmt = (
        select(RiskFeatureSnapshot)
        .where(RiskFeatureSnapshot.organization_id == organization_id)
        .order_by(RiskFeatureSnapshot.period_date.desc())
    )

    return db.scalars(stmt).all()


@router.post("", response_model=RiskFeatureSnapshotItem, status_code=201)
def create_feature_snapshot(
    organization_id: UUID,
    payload: RiskFeatureSnapshotCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    snapshot = RiskFeatureSnapshot(
        organization_id=organization_id,
        import_batch_id=None,
        period_date=payload.period_date,
        revenue=payload.revenue,
        debt_amount=payload.debt_amount,
        overdue_days_30=payload.overdue_days_30,
        overdue_days_90=payload.overdue_days_90,
        disputes_count=payload.disputes_count,
        transactions_count=payload.transactions_count,
        employees_count=payload.employees_count,
        raw_features=payload.raw_features,
    )

    db.add(snapshot)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Feature snapshot for this organization and period already exists",
        )

    db.refresh(snapshot)

    return snapshot