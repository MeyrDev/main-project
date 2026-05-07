from app.models import ( 
    Organization, 
)
from decimal import Decimal

def seed_organizations(db):
    organizations_data = [
        {
            "bin": "240101000001",
            "name": "ТОО Alatau Logistics",
            "industry": "Логистика",
            "region": "Алматы",
            "segment": "Средний бизнес",
            "annual_revenue": Decimal("185000000.00"),
            "employees_count": 85,
            "status": "active",
        },
        {
            "bin": "240101000002",
            "name": "ТОО Astana Retail Group",
            "industry": "Розничная торговля",
            "region": "Астана",
            "segment": "Крупный бизнес",
            "annual_revenue": Decimal("620000000.00"),
            "employees_count": 240,
            "status": "active",
        },
        {
            "bin": "240101000003",
            "name": "ТОО Caspian Agro",
            "industry": "Сельское хозяйство",
            "region": "Атырауская область",
            "segment": "Средний бизнес",
            "annual_revenue": Decimal("95000000.00"),
            "employees_count": 54,
            "status": "active",
        },
        {
            "bin": "240101000004",
            "name": "ТОО Steppe Construction",
            "industry": "Строительство",
            "region": "Караганда",
            "segment": "Средний бизнес",
            "annual_revenue": Decimal("130000000.00"),
            "employees_count": 73,
            "status": "active",
        },
        {
            "bin": "240101000005",
            "name": "ТОО QazTech Service",
            "industry": "IT-услуги",
            "region": "Алматы",
            "segment": "Малый бизнес",
            "annual_revenue": Decimal("45000000.00"),
            "employees_count": 28,
            "status": "active",
        },
    ]

    organizations = {}

    for item in organizations_data:
        organization = db.query(Organization).filter(
            Organization.bin == item["bin"]
        ).first()

        if organization is None:
            organization = Organization(**item)
            db.add(organization)
            db.flush()

        organizations[item["bin"]] = organization

    return organizations