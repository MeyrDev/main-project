# risk-crm-starter

Минимальный технический каркас для приложения к диссертации:

**Тема:** Исследование моделей и методов для разработки CRM-системы прогнозирования рисков хозяйствующих субъектов.

## Что входит

- PostgreSQL в Docker Compose
- Python backend-контейнер
- SQLAlchemy 2.x ORM-модели
- Alembic миграции
- доменная модель под CRM + risk prediction:
  - companies
  - company_feature_snapshots
  - ml_models
  - risk_predictions

## Быстрый старт

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec app alembic upgrade head
```

Проверить подключение:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "\dt"
```

Остановить:

```bash
docker compose down
```

Остановить и удалить данные БД:

```bash
docker compose down -v
```

## Создание новой миграции после изменения моделей

```bash
docker compose exec app alembic revision --autogenerate -m "change schema"
docker compose exec app alembic upgrade head
```

## Локальный запуск без Docker для backend

```bash
python -m venv .venv
. .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows PowerShell

pip install -e .
cp .env.example .env
alembic upgrade head
```

Контейнер `app` на этом этапе держится запущенным специально, чтобы из него можно было выполнять Alembic-команды.
