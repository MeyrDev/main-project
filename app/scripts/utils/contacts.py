from app.models import ( 
    OrganizationContact, 
) 

def seed_contacts(db, organizations):
    contacts_data = [
        {
            "organization": organizations["240101000001"],
            "full_name": "Ерлан Смагулов",
            "position": "Финансовый директор",
            "email": "finance@alatau-logistics.local",
            "phone": "+7 701 000 00 01",
        },
        {
            "organization": organizations["240101000002"],
            "full_name": "Айжан Муратова",
            "position": "Руководитель отдела продаж",
            "email": "sales@astana-retail.local",
            "phone": "+7 701 000 00 02",
        },
        {
            "organization": organizations["240101000003"],
            "full_name": "Нурлан Ахметов",
            "position": "Директор",
            "email": "director@caspian-agro.local",
            "phone": "+7 701 000 00 03",
        },
    ]

    for item in contacts_data:
        existing = db.query(OrganizationContact).filter(
            OrganizationContact.organization_id == item["organization"].id,
            OrganizationContact.email == item["email"],
        ).first()

        if existing is None:
            contact = OrganizationContact(
                organization_id=item["organization"].id,
                full_name=item["full_name"],
                position=item["position"],
                email=item["email"],
                phone=item["phone"],
                is_primary=True,
            )
            db.add(contact)