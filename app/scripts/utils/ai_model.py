from app.models import ( 
    MLModel, 
    RiskFeatureSnapshot,
    RiskLevel,
    RiskPrediction
) 
from datetime import date, datetime, timezone
from decimal import Decimal

def seed_ml_model(db):
    model = db.query(MLModel).filter(
        MLModel.name == "risk_classifier",
        MLModel.version == "1.0.0",
    ).first()

    if model is None:
        model = MLModel(
            name="risk_classifier",
            version="1.0.0",
            algorithm_name="LogisticRegression",
            target_name="default_risk",
            artifact_path="artifacts/risk_model.pkl",
            metrics={
                "roc_auc": 0.83,
                "pr_auc": 0.39,
                "f1": 0.71,
                "brier_score": 0.12,
            },
            parameters={
                "max_iter": 1000,
                "class_weight": "balanced",
            },
            trained_at=datetime.now(timezone.utc),
        )
        db.add(model)
        db.flush()

    return model


def seed_features_and_predictions(db, organizations, import_batch, model):
    data = [
        {
            "bin": "240101000001",
            "period_date": date(2026, 1, 1),
            "revenue": Decimal("185000000.00"),
            "debt_amount": Decimal("18000000.00"),
            "overdue_days_30": 2,
            "overdue_days_90": 0,
            "disputes_count": 1,
            "transactions_count": 124,
            "employees_count": 85,
            "risk_score": Decimal("0.18000"),
            "risk_level": RiskLevel.low,
        },
        {
            "bin": "240101000002",
            "period_date": date(2026, 1, 1),
            "revenue": Decimal("620000000.00"),
            "debt_amount": Decimal("98000000.00"),
            "overdue_days_30": 12,
            "overdue_days_90": 3,
            "disputes_count": 4,
            "transactions_count": 380,
            "employees_count": 240,
            "risk_score": Decimal("0.47000"),
            "risk_level": RiskLevel.medium,
        },
        {
            "bin": "240101000003",
            "period_date": date(2026, 1, 1),
            "revenue": Decimal("95000000.00"),
            "debt_amount": Decimal("52000000.00"),
            "overdue_days_30": 35,
            "overdue_days_90": 14,
            "disputes_count": 7,
            "transactions_count": 61,
            "employees_count": 54,
            "risk_score": Decimal("0.76000"),
            "risk_level": RiskLevel.high,
        },
        {
            "bin": "240101000004",
            "period_date": date(2026, 1, 1),
            "revenue": Decimal("130000000.00"),
            "debt_amount": Decimal("90000000.00"),
            "overdue_days_30": 48,
            "overdue_days_90": 28,
            "disputes_count": 11,
            "transactions_count": 44,
            "employees_count": 73,
            "risk_score": Decimal("0.91000"),
            "risk_level": RiskLevel.critical,
        },
        {
            "bin": "240101000005",
            "period_date": date(2026, 1, 1),
            "revenue": Decimal("45000000.00"),
            "debt_amount": Decimal("5000000.00"),
            "overdue_days_30": 0,
            "overdue_days_90": 0,
            "disputes_count": 0,
            "transactions_count": 96,
            "employees_count": 28,
            "risk_score": Decimal("0.09000"),
            "risk_level": RiskLevel.low,
        },
    ]

    for item in data:
        organization = organizations[item["bin"]]

        snapshot = db.query(RiskFeatureSnapshot).filter(
            RiskFeatureSnapshot.organization_id == organization.id,
            RiskFeatureSnapshot.period_date == item["period_date"],
        ).first()

        if snapshot is None:
            snapshot = RiskFeatureSnapshot(
                organization_id=organization.id,
                import_batch_id=import_batch.id,
                period_date=item["period_date"],
                revenue=item["revenue"],
                debt_amount=item["debt_amount"],
                overdue_days_30=item["overdue_days_30"],
                overdue_days_90=item["overdue_days_90"],
                disputes_count=item["disputes_count"],
                transactions_count=item["transactions_count"],
                employees_count=item["employees_count"],
                raw_features={
                    "source": "seed.py",
                    "note": "Демонстрационный набор признаков риска",
                },
            )
            db.add(snapshot)
            db.flush()

        prediction = db.query(RiskPrediction).filter(
            RiskPrediction.organization_id == organization.id,
            RiskPrediction.feature_snapshot_id == snapshot.id,
            RiskPrediction.model_id == model.id,
        ).first()

        if prediction is None:
            prediction = RiskPrediction(
                organization_id=organization.id,
                feature_snapshot_id=snapshot.id,
                model_id=model.id,
                risk_score=item["risk_score"],
                risk_level=item["risk_level"],
                explanation={
                    "main_factors": [
                        "доля задолженности",
                        "просрочки платежей",
                        "количество спорных ситуаций",
                    ],
                    "comment": "Оценка рассчитана демонстрационной ML-моделью",
                },
                recommendations={
                    "actions": [
                        "провести дополнительную проверку финансовой отчетности",
                        "ограничить кредитный лимит при высоком риске",
                        "усилить мониторинг платежной дисциплины",
                    ]
                },
            )
            db.add(prediction)