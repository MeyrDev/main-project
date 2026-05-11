"""
Скрипт демонстрационного заполнения базы данных.

Создаёт роли, пользователей, организации, контакты, сделки,
источники данных, признаки риска, ML-модель и тестовые risk_predictions.
Используется для локального запуска и демонстрации приложения.
"""
from datetime import datetime, timezone 

from app.db.session import SessionLocal
from app.models import (
    DataImportBatch, 
    ImportStatus, 
) 
from app.scripts.utils.roles_users import seed_roles, seed_users
from app.scripts.utils.sources import seed_external_sources
from app.scripts.utils.organizations import seed_organizations
from app.scripts.utils.contacts import seed_contacts
from app.scripts.utils.ai_model import seed_ml_model, seed_features_and_predictions
from app.scripts.utils.deals import seed_deals_and_interactions

def seed_import_batch(db, sources, users):
    source = sources["financial_reports"]
    uploaded_by = users["analyst@risk-crm.local"]

    batch = db.query(DataImportBatch).filter(
        DataImportBatch.source_id == source.id,
        DataImportBatch.file_name == "demo_financial_features.csv",
    ).first()

    if batch is None:
        batch = DataImportBatch(
            source_id=source.id,
            uploaded_by_id=uploaded_by.id,
            file_name="demo_financial_features.csv",
            status=ImportStatus.success,
            rows_total=5,
            rows_success=5,
            rows_failed=0,
            error_message=None,
            meta={
                "description": "Демонстрационный импорт признаков риска",
                "source": "seed.py",
            },
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        db.add(batch)
        db.flush()

    return batch 

def main():
    db = SessionLocal()

    try:
        roles = seed_roles(db)
        users = seed_users(db, roles)
        sources = seed_external_sources(db)
        organizations = seed_organizations(db)

        seed_contacts(db, organizations)

        model = seed_ml_model(db)
        import_batch = seed_import_batch(db, sources, users)

        seed_features_and_predictions(db, organizations, import_batch, model)
        seed_deals_and_interactions(db, organizations, users)

        db.commit()

        print("Seed data inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()