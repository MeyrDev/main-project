from app.models import ( 
    DataSourceType, 
    ExternalDataSource, 
) 

def seed_external_sources(db):
    sources_data = [
        {
            "code": "crm_manual",
            "name": "Ручной ввод CRM-данных",
            "source_type": DataSourceType.crm,
            "description": "Данные, введенные пользователями CRM-системы",
        },
        {
            "code": "financial_reports",
            "name": "Финансовая отчетность",
            "source_type": DataSourceType.financial_report,
            "description": "Финансовые показатели организаций",
        },
        {
            "code": "external_registry",
            "name": "Внешний реестр организаций",
            "source_type": DataSourceType.external_registry,
            "description": "Справочные данные из внешних источников",
        },
    ]

    sources = {}

    for item in sources_data:
        source = db.query(ExternalDataSource).filter(
            ExternalDataSource.code == item["code"]
        ).first()

        if source is None:
            source = ExternalDataSource(
                code=item["code"],
                name=item["name"],
                source_type=item["source_type"],
                description=item["description"],
                connection_config=None,
                is_active=True,
            )
            db.add(source)
            db.flush()

        sources[item["code"]] = source

    return sources
