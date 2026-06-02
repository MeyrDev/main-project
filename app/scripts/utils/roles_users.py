from app.models import (
    Role,
    User,
)
from app.core.security import get_password_hash

def seed_roles(db):
    roles_data = [
        {
            "code": "admin",
            "name": "Администратор",
            "description": "Управление пользователями, ролями и настройками системы",
        },
        {
            "code": "manager",
            "name": "Менеджер",
            "description": "Работа с организациями, сделками и взаимодействиями",
        },
        {
            "code": "analyst",
            "name": "Аналитик",
            "description": "Анализ показателей, рисков и отчетов",
        },
        {
            "code": "ai_specialist",
            "name": "Специалист ИИ",
            "description": "Обучение и сопровождение ML-моделей",
        },
        {
            "code": "decision_maker",
            "name": "Лицо, принимающее решение",
            "description": "Просмотр итоговой оценки риска и принятие решений",
        },
    ]

    roles = {}

    for item in roles_data:
        role = db.query(Role).filter(Role.code == item["code"]).first()

        if role is None:
            role = Role(**item)
            db.add(role)
            db.flush()

        roles[item["code"]] = role

    return roles


def seed_users(db, roles):
    users_data = [
        {
            "email": "admin@risk-crm.local",
            "full_name": "Администратор системы",
            "role": roles["admin"],
            "password": "admin123",
        },
        {
            "email": "manager@risk-crm.local",
            "full_name": "CRM-менеджер",
            "role": roles["manager"],
        },
        {
            "email": "analyst@risk-crm.local",
            "full_name": "Финансовый аналитик",
            "role": roles["analyst"],
        },
        {
            "email": "ml@risk-crm.local",
            "full_name": "Специалист по ИИ",
            "role": roles["ai_specialist"],
        },
    ]

    users = {}

    for item in users_data:
        user = db.query(User).filter(User.email == item["email"]).first()

        if user is None:
            user = User(
                email=item["email"],
                full_name=item["full_name"],
                role_id=item["role"].id,
                password_hash=get_password_hash(item["password"])
                if item.get("password")
                else None,
                is_active=True,
            )
            db.add(user)
            db.flush()
        elif item.get("password") and not user.password_hash:
            user.password_hash = get_password_hash(item["password"])

        users[item["email"]] = user

    return users
