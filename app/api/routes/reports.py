"""
API для работы с отчётами.

Содержит методы создания отчёта, просмотра списка отчётов,
получения конкретного отчёта и формирования данных отчёта.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import (
    MLModel,
    Organization,
    Report,
    ReportStatus,
    ReportType,
    RiskFeatureSnapshot,
    RiskPrediction,
    User,
)
from app.schemas import ReportCreate, ReportData, ReportItem
from app.services.audit import create_audit_log

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=list[ReportItem])
def get_reports(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = (
        select(Report)
        .order_by(Report.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(stmt).all()


@router.post("", response_model=ReportItem, status_code=201)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
):
    if payload.organization_id is not None:
        organization = db.get(Organization, payload.organization_id)

        if organization is None:
            raise HTTPException(status_code=404, detail="Organization not found")

    if payload.created_by_id is not None:
        user = db.get(User, payload.created_by_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    if payload.report_type in {
        ReportType.organization_card,
        ReportType.risk_summary,
    } and payload.organization_id is None:
        raise HTTPException(
            status_code=400,
            detail="organization_id is required for this report type",
        )

    report = Report(
        organization_id=payload.organization_id,
        created_by_id=payload.created_by_id,
        title=payload.title,
        report_type=payload.report_type,
        status=ReportStatus.ready,
        parameters=payload.parameters,
        file_path=None,
    )

    db.add(report)
    db.flush()

    create_audit_log(
        db=db,
        action="report.created",
        entity_type="report",
        entity_id=report.id,
        user_id=report.created_by_id,
        details={
            "title": report.title,
            "report_type": report.report_type.value,
            "organization_id": str(report.organization_id)
            if report.organization_id is not None
            else None,
        },
    )
    db.commit()
    db.refresh(report)

    return report


@router.get("/{report_id}", response_model=ReportItem)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
):
    report = db.get(Report, report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.get("/{report_id}/data", response_model=ReportData)
def get_report_data(
    report_id: UUID,
    db: Session = Depends(get_db),
):
    report = db.get(Report, report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.report_type == ReportType.risk_summary:
        content = build_risk_summary_report(report, db)

    elif report.report_type == ReportType.organization_card:
        content = build_organization_card_report(report, db)

    elif report.report_type == ReportType.portfolio_analytics:
        content = build_portfolio_analytics_report(db)

    elif report.report_type == ReportType.model_quality:
        content = build_model_quality_report(db)

    else:
        content = {
            "message": "Unsupported report type",
        }

    return ReportData(
        id=report.id,
        title=report.title,
        report_type=report.report_type,
        status=report.status,
        generated_at=datetime.now(timezone.utc),
        parameters=report.parameters,
        content=content,
    )


def build_risk_summary_report(report: Report, db: Session) -> dict:
    if report.organization_id is None:
        raise HTTPException(
            status_code=400,
            detail="organization_id is required for risk_summary report",
        )

    organization = db.get(Organization, report.organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    latest_prediction = db.scalars(
        select(RiskPrediction)
        .where(RiskPrediction.organization_id == organization.id)
        .order_by(RiskPrediction.predicted_at.desc())
        .limit(1)
    ).first()

    risk_history = db.scalars(
        select(RiskPrediction)
        .where(RiskPrediction.organization_id == organization.id)
        .order_by(RiskPrediction.predicted_at.desc())
    ).all()

    feature_snapshots = db.scalars(
        select(RiskFeatureSnapshot)
        .where(RiskFeatureSnapshot.organization_id == organization.id)
        .order_by(RiskFeatureSnapshot.period_date.desc())
    ).all()

    return {
        "organization": {
            "id": str(organization.id),
            "bin": organization.bin,
            "name": organization.name,
            "industry": organization.industry,
            "region": organization.region,
            "segment": organization.segment,
            "status": organization.status,
            "annual_revenue": str(organization.annual_revenue)
            if organization.annual_revenue is not None
            else None,
            "employees_count": organization.employees_count,
        },
        "latest_risk": serialize_prediction(latest_prediction),
        "risk_history": [
            serialize_prediction(prediction)
            for prediction in risk_history
        ],
        "feature_snapshots": [
            {
                "id": str(snapshot.id),
                "period_date": snapshot.period_date.isoformat(),
                "revenue": str(snapshot.revenue)
                if snapshot.revenue is not None
                else None,
                "debt_amount": str(snapshot.debt_amount)
                if snapshot.debt_amount is not None
                else None,
                "overdue_days_30": snapshot.overdue_days_30,
                "overdue_days_90": snapshot.overdue_days_90,
                "disputes_count": snapshot.disputes_count,
                "transactions_count": snapshot.transactions_count,
                "employees_count": snapshot.employees_count,
            }
            for snapshot in feature_snapshots
        ],
        "conclusion": build_risk_conclusion(latest_prediction),
    }


def build_organization_card_report(report: Report, db: Session) -> dict:
    if report.organization_id is None:
        raise HTTPException(
            status_code=400,
            detail="organization_id is required for organization_card report",
        )

    organization = db.get(Organization, report.organization_id)

    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "organization": {
            "id": str(organization.id),
            "bin": organization.bin,
            "name": organization.name,
            "industry": organization.industry,
            "region": organization.region,
            "segment": organization.segment,
            "status": organization.status,
            "annual_revenue": str(organization.annual_revenue)
            if organization.annual_revenue is not None
            else None,
            "employees_count": organization.employees_count,
            "description": organization.description,
        }
    }


def build_portfolio_analytics_report(db: Session) -> dict:
    organizations_count = db.scalar(
        select(func.count()).select_from(Organization)
    ) or 0

    predictions_count = db.scalar(
        select(func.count()).select_from(RiskPrediction)
    ) or 0

    distribution_rows = db.execute(
        select(RiskPrediction.risk_level, func.count(RiskPrediction.id))
        .group_by(RiskPrediction.risk_level)
        .order_by(RiskPrediction.risk_level)
    ).all()

    risk_distribution = [
        {
            "risk_level": row[0].value,
            "count": row[1],
        }
        for row in distribution_rows
    ]

    return {
        "organizations_count": organizations_count,
        "predictions_count": predictions_count,
        "risk_distribution": risk_distribution,
    }


def build_model_quality_report(db: Session) -> dict:
    model = db.scalars(
        select(MLModel)
        .order_by(MLModel.created_at.desc())
        .limit(1)
    ).first()

    if model is None:
        return {
            "message": "No ML model information found in database",
        }

    return {
        "model": {
            "id": str(model.id),
            "name": model.name,
            "version": model.version,
            "algorithm_name": model.algorithm_name,
            "target_name": model.target_name,
            "artifact_path": model.artifact_path,
            "metrics": model.metrics,
            "parameters": model.parameters,
            "trained_at": model.trained_at.isoformat()
            if model.trained_at is not None
            else None,
        }
    }


def serialize_prediction(prediction: RiskPrediction | None) -> dict | None:
    if prediction is None:
        return None

    return {
        "id": str(prediction.id),
        "risk_score": str(prediction.risk_score),
        "risk_level": prediction.risk_level.value,
        "predicted_at": prediction.predicted_at.isoformat(),
        "explanation": prediction.explanation,
        "recommendations": prediction.recommendations,
    }


def build_risk_conclusion(prediction: RiskPrediction | None) -> str:
    if prediction is None:
        return "По организации ещё не рассчитана оценка риска."

    risk_level = prediction.risk_level.value

    if risk_level == "low":
        return "Организация имеет низкий уровень риска. Возможно стандартное обслуживание."

    if risk_level == "medium":
        return "Организация имеет средний уровень риска. Рекомендуется дополнительный мониторинг."

    if risk_level == "high":
        return "Организация имеет высокий уровень риска. Рекомендуется усиленная проверка."

    return "Организация имеет критический уровень риска. Рекомендуется ограничить рискованные операции."