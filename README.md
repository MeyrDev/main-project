# risk-crm-starter

Технический каркас приложения к диссертации.

**Тема диссертации:**  
«Исследование моделей и методов для разработки CRM-системы прогнозирования рисков хозяйствующих субъектов».

Проект предназначен для локального развёртывания CRM-системы с модулем прогнозирования рисков.  
На текущем этапе реализованы:

- PostgreSQL в Docker Compose;
- Python backend-контейнер;
- SQLAlchemy ORM-модели;
- Alembic-миграции;
- seed-скрипт для демонстрационных данных;
- структура БД под CRM-систему и ML-модуль прогнозирования рисков.

---

## Быстрый запуск всего проекта

Проект состоит из трёх основных сервисов:

- `db` — PostgreSQL;
- `app` — FastAPI backend;
- `web` — React frontend.

Первый запуск проекта:

```bash
cp .env.example .env
cp web/.env.example web/.env
make init

## 1. Основные таблицы БД

Текущая схема базы данных включает:

```text
roles
users
organizations
organization_contacts
deals
interactions
external_data_sources
data_import_batches
risk_feature_snapshots
ml_models
risk_predictions
reports
audit_logs
alembic_version
```

Кратко:

```text
roles                      — роли пользователей системы
users                      — пользователи CRM
organizations              — хозяйствующие субъекты / организации
organization_contacts      — контактные лица организаций
deals                      — сделки с организациями
interactions               — история взаимодействий
external_data_sources      — внешние источники данных
data_import_batches        — пакеты импорта данных
risk_feature_snapshots     — признаки риска по организациям
ml_models                  — сведения о ML-моделях
risk_predictions           — результаты прогнозирования риска
reports                    — отчёты
audit_logs                 — журнал действий пользователей
```

---

## 2. Первый запуск проекта

Скопировать переменные окружения:

```bash
cp .env.example .env
```

Запустить контейнеры:

```bash
docker compose up -d --build
```

Проверить состояние контейнеров:

```bash
docker compose ps
```

---

## 3. Применение миграций

Миграции создают структуру базы данных: таблицы, связи, индексы, enum-типы и ограничения.

Если контейнер `app` запущен:

```bash
docker compose exec app alembic upgrade head
```

Если контейнер `app` не запущен:

```bash
docker compose run --rm app alembic upgrade head
```

Проверить текущую ревизию Alembic:

```bash
docker compose run --rm app alembic current
```

---

## 4. Заполнение базы демонстрационными данными

Seed-скрипт добавляет тестовые данные: роли, пользователей, организации, сделки, признаки риска, ML-модель и результаты прогнозирования.

Если контейнер `app` запущен:

```bash
docker compose exec app python -m app.scripts.seed
```

Если контейнер `app` не запущен:

```bash
docker compose run --rm app python -m app.scripts.seed
```

После успешного выполнения должно появиться сообщение:

```text
Seed data inserted successfully.
```

---

## 5. Проверка таблиц и данных

Посмотреть список таблиц:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "\\dt"
```

Проверить организации:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "SELECT name, industry, region FROM organizations;"
```

Проверить пользователей:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "SELECT email, full_name FROM users;"
```

Проверить риск-оценки:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "SELECT risk_score, risk_level FROM risk_predictions;"
```

---

## 6. Подключение через DBeaver

Если в `docker-compose.yml` указан порт:

```yaml
ports:
  - "5433:5432"
```

то настройки DBeaver:

```text
Host: localhost
Port: 5433
Database: risk_crm
Username: risk_user
Password: risk_password
```

Если в `docker-compose.yml` указан порт:

```yaml
ports:
  - "5432:5432"
```

то в DBeaver нужно использовать:

```text
Port: 5432
```

Путь в DBeaver:

```text
Database → New Database Connection → PostgreSQL
```

После подключения открыть:

```text
risk_crm → Schemas → public → Tables
```

---

## 7. Полный запуск с нуля

Использовать, если база ещё не нужна или её можно удалить.

```bash
docker compose down -v
docker compose up -d --build
docker compose run --rm app alembic upgrade head
docker compose run --rm app python -m app.scripts.seed
```

Проверить:

```bash
docker compose exec db psql -U risk_user -d risk_crm -c "\\dt"
```

---

## 8. Обычный запуск после первого раза

Если база уже создана и данные уже загружены:

```bash
docker compose up -d
```

Проверить контейнеры:

```bash
docker compose ps
```

Остановить контейнеры без удаления данных:

```bash
docker compose down
```

---

## 9. Остановить и удалить базу данных

Эта команда удалит Docker volume с данными PostgreSQL:

```bash
docker compose down -v
```

После этого при следующем запуске нужно снова выполнить:

```bash
docker compose up -d --build
docker compose run --rm app alembic upgrade head
docker compose run --rm app python -m app.scripts.seed
```

---

## 10. Создание новой миграции после изменения моделей

После изменения файлов в `app/models/` создать новую миграцию:

```bash
docker compose run --rm app alembic revision --autogenerate -m "change schema"
```

Применить миграцию:

```bash
docker compose run --rm app alembic upgrade head
```

Если контейнер `app` запущен:

```bash
docker compose exec app alembic revision --autogenerate -m "change schema"
docker compose exec app alembic upgrade head
```

---

## 11. Развёртывание на другой локальной машине

На другой машине выполнить:

```bash
git clone <адрес-репозитория>
cd risk-crm-starter
cp .env.example .env
docker compose up -d --build
docker compose run --rm app alembic upgrade head
docker compose run --rm app python -m app.scripts.seed
```

После этого база будет создана и заполнена демонстрационными данными.

Важно:

```text
Alembic-миграции создают структуру БД.
seed.py добавляет демонстрационные данные.
pg_dump нужен для переноса реальной заполненной базы.
```

---

## 12. Перенос реальных данных на другую машину

На старой машине создать backup:

```bash
docker compose exec db pg_dump -U risk_user -d risk_crm > risk_crm_backup.sql
```

На новой машине поднять контейнеры:

```bash
docker compose up -d --build
```

Восстановить backup:

```bash
docker compose exec -T db psql -U risk_user -d risk_crm < risk_crm_backup.sql
```

---

## 13. Локальный запуск без Docker

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Linux / Mac:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\\Scripts\\activate
```

Установить зависимости:

```bash
pip install -e .
```

Скопировать `.env`:

```bash
cp .env.example .env
```

Применить миграции:

```bash
alembic upgrade head
```

Запустить seed:

```bash
python -m app.scripts.seed
```

Для локального запуска без Docker PostgreSQL должен быть установлен и запущен отдельно.

---

## 14. Частые проблемы

### service "app" is not running

Если команда:

```bash
docker compose exec app python -m app.scripts.seed
```

выдаёт:

```text
service "app" is not running
```

использовать одноразовый запуск:

```bash
docker compose run --rm app python -m app.scripts.seed
```

То же самое для Alembic:

```bash
docker compose run --rm app alembic upgrade head
```

---

### Ошибка PostgreSQL volume после смены версии

Если PostgreSQL-контейнер не запускается после смены версии образа, удалить volume:

```bash
docker compose down -v
docker compose up -d --build
```

Для учебного проекта рекомендуется использовать стабильный образ:

```yaml
image: postgres:16-alpine
```

---

## 15. Структура проекта

```text
risk-crm-starter/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── audit_log.py
│   │   ├── data_import_batch.py
│   │   ├── deal.py
│   │   ├── external_data_source.py
│   │   ├── feature_snapshot.py
│   │   ├── interaction.py
│   │   ├── ml_model.py
│   │   ├── organization.py
│   │   ├── organization_contact.py
│   │   ├── report.py
│   │   ├── risk_prediction.py
│   │   ├── role.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── scripts/
│   │   ├── seed.py
│   │   └── __init__.py
│   └── main.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 16. Следующий этап разработки

После настройки базы данных следующий этап — разработка минимального backend API:

```text
GET /api/organizations
GET /api/organizations/{id}
GET /api/organizations/{id}/risk
GET /api/risk-predictions
GET /api/dashboard/summary
```

Затем будет добавлен ML-модуль:

```text
POST /api/ml/predict/{organization_id}
```

Он будет брать признаки из `risk_feature_snapshots`, загружать модель из `ml_models` и сохранять результат в `risk_predictions`.
