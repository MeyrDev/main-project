from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.api.deps import get_db
from app.models import AuditLog, Deal, Organization, RiskPrediction, User
from app.schemas import (
    DashboardHighRiskOrganization,
    DashboardRecentAuditLog,
    DashboardRecentPrediction,
    DashboardSummary,
    RiskLevelCount,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    organizations_count = db.scalar(select(func.count()).select_from(Organization)) or 0
    users_count = db.scalar(select(func.count()).select_from(User)) or 0
    deals_count = db.scalar(select(func.count()).select_from(Deal)) or 0
    predictions_count = db.scalar(select(func.count()).select_from(RiskPrediction)) or 0

    risk_distribution = get_risk_distribution(db)
    high_risk_organizations = get_high_risk_organizations(db)
    recent_predictions = get_recent_predictions(db)
    recent_audit_logs = get_recent_audit_logs(db)

    return DashboardSummary(
        organizations_count=organizations_count,
        users_count=users_count,
        deals_count=deals_count,
        predictions_count=predictions_count,
        risk_distribution=risk_distribution,
        high_risk_organizations=high_risk_organizations,
        recent_predictions=recent_predictions,
        recent_audit_logs=recent_audit_logs,
    )


def get_risk_distribution(db: Session) -> list[RiskLevelCount]:
    stmt = (
        select(RiskPrediction.risk_level, func.count(RiskPrediction.id))
        .group_by(RiskPrediction.risk_level)
        .order_by(RiskPrediction.risk_level)
    )

    result = []

    for level, count in db.execute(stmt).all():
        risk_level = level.value if hasattr(level, "value") else str(level)

        result.append(
            RiskLevelCount(
                risk_level=risk_level,
                count=count,
            )
        )

    return result


def get_high_risk_organizations(db: Session) -> list[DashboardHighRiskOrganization]:
    latest_predictions_subquery = (
        select(
            RiskPrediction.organization_id,
            func.max(RiskPrediction.predicted_at).label("latest_predicted_at"),
        )
        .group_by(RiskPrediction.organization_id)
        .subquery()
    )

    stmt = (
        select(Organization, RiskPrediction)
        .join(
            latest_predictions_subquery,
            latest_predictions_subquery.c.organization_id == Organization.id,
        )
        .join(
            RiskPrediction,
            and_(
                RiskPrediction.organization_id == Organization.id,
                RiskPrediction.predicted_at
                == latest_predictions_subquery.c.latest_predicted_at,
            ),
        )
        .order_by(RiskPrediction.risk_score.desc())
        .limit(5)
    )

    result = []

    for organization, prediction in db.execute(stmt).all():
        risk_level = (
            prediction.risk_level.value
            if hasattr(prediction.risk_level, "value")
            else str(prediction.risk_level)
        )

        result.append(
            DashboardHighRiskOrganization(
                organization_id=organization.id,
                organization_name=organization.name,
                industry=organization.industry,
                region=organization.region,
                risk_score=prediction.risk_score,
                risk_level=risk_level,
                predicted_at=prediction.predicted_at,
            )
        )

    return result


def get_recent_predictions(db: Session) -> list[DashboardRecentPrediction]:
    stmt = (
        select(Organization, RiskPrediction)
        .join(RiskPrediction, RiskPrediction.organization_id == Organization.id)
        .order_by(RiskPrediction.predicted_at.desc())
        .limit(5)
    )

    result = []

    for organization, prediction in db.execute(stmt).all():
        risk_level = (
            prediction.risk_level.value
            if hasattr(prediction.risk_level, "value")
            else str(prediction.risk_level)
        )

        result.append(
            DashboardRecentPrediction(
                prediction_id=prediction.id,
                organization_id=organization.id,
                organization_name=organization.name,
                risk_score=prediction.risk_score,
                risk_level=risk_level,
                predicted_at=prediction.predicted_at,
            )
        )

    return result


def get_recent_audit_logs(db: Session) -> list[DashboardRecentAuditLog]:
    stmt = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )

    result = []

    for audit_log in db.scalars(stmt).all():
        result.append(
            DashboardRecentAuditLog(
                id=audit_log.id,
                action=audit_log.action,
                entity_type=audit_log.entity_type,
                entity_id=audit_log.entity_id,
                details=audit_log.details,
                created_at=audit_log.created_at,
            )
        )

    return result