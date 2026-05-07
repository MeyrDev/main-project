from app.models import ( 
    Deal,
    DealStage, 
    Interaction,
    InteractionType,
)
from datetime import date, datetime, timezone
from decimal import Decimal

def seed_deals_and_interactions(db, organizations, users):
    manager = users["manager@risk-crm.local"]

    deals_data = [
        {
            "organization": organizations["240101000001"],
            "title": "Договор на логистическое обслуживание",
            "stage": DealStage.approved,
            "amount": Decimal("12000000.00"),
        },
        {
            "organization": organizations["240101000002"],
            "title": "Поставка оборудования для торговых точек",
            "stage": DealStage.negotiation,
            "amount": Decimal("35000000.00"),
        },
        {
            "organization": organizations["240101000004"],
            "title": "Кредитная линия на строительный проект",
            "stage": DealStage.new,
            "amount": Decimal("80000000.00"),
        },
    ]

    for item in deals_data:
        deal = db.query(Deal).filter(
            Deal.organization_id == item["organization"].id,
            Deal.title == item["title"],
        ).first()

        if deal is None:
            deal = Deal(
                organization_id=item["organization"].id,
                owner_id=manager.id,
                title=item["title"],
                stage=item["stage"],
                amount=item["amount"],
                currency="KZT",
                expected_close_date=date(2026, 3, 1),
                description="Демонстрационная сделка для CRM-модуля",
            )
            db.add(deal)
            db.flush()

        interaction = db.query(Interaction).filter(
            Interaction.organization_id == item["organization"].id,
            Interaction.subject == "Первичный контакт с организацией",
        ).first()

        if interaction is None:
            interaction = Interaction(
                organization_id=item["organization"].id,
                user_id=manager.id,
                deal_id=deal.id,
                interaction_type=InteractionType.call,
                subject="Первичный контакт с организацией",
                description="Менеджер уточнил данные по сделке и финансовым показателям.",
                happened_at=datetime.now(timezone.utc),
            )
            db.add(interaction)