# Контекст проекта для ChatGPT

## 1. Название и цель проекта

Проект: `risk-crm-starter` / EntityRisk Analytics.

Цель: CRM-система для учета хозяйствующих субъектов, сделок, взаимодействий и прогнозирования риска организации с помощью ML-модели. Проект используется как магистерский/диссертационный прототип CRM-системы прогнозирования рисков.

## 2. Бизнес-логика

Система хранит организации, контакты, сделки, взаимодействия, финансово-операционные признаки риска, прогнозы риска, отчеты и аудит действий. Для организации можно:

- вести карточку организации;
- добавлять сделки и взаимодействия;
- сохранять снимки риск-признаков за период;
- запускать prediction риска;
- смотреть текущий риск и историю прогнозов;
- формировать отчеты;
- просматривать audit log.

Риск выражается через `risk_score` от `0` до `1` и уровень `risk_level`: `low`, `medium`, `high`, `critical`.

## 3. Технологический стек

Backend:

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic Settings
- Passlib + bcrypt
- Basic Auth

ML:

- pandas
- numpy
- scikit-learn
- joblib
- `GradientBoostingClassifier`
- `CalibratedClassifierCV(method="isotonic")`

Frontend:

- React 19
- TypeScript
- Vite
- CSS

Инфраструктура:

- Docker
- Docker Compose
- Makefile

## 4. Структура папок

```text
app/                       FastAPI backend
app/api/                   API router, dependencies, routes
app/api/routes/            Endpoint-модули
app/core/                  Config и security helpers
app/db/                    SQLAlchemy Base и session
app/models/                ORM-модели БД
app/schemas/               Pydantic-схемы
app/services/              Сервисные функции, сейчас в основном audit
app/ml/                    ML-пайплайн: подготовка датасетов, обучение, prediction
app/scripts/               Seed-скрипты и demo-data helpers
alembic/                   Alembic migrations
artifacts/                 ML artifact и отчеты обучения
data/raw/                  Исходный CSV, сейчас data/raw/risk_dataset.csv
data/                      Подготовленные train/validation датасеты
web/                       React/Vite frontend
web/src/pages/             Основные страницы
web/src/features/          Feature-компоненты frontend
web/src/api/               Frontend API client
docs/                      Документация
```

Не анализировать как часть проекта: `.venv`, `node_modules`, `__pycache__`, `build`, `dist`.

## 5. Backend-модули и endpoints

Backend стартует из `app/main.py`. Основной router находится в `app/api/router.py`, API-префикс: `/api`.

Health:

- `GET /health`

Auth:

- `GET /api/auth/me` - текущий пользователь по Basic Auth.

Organizations:

- `GET /api/organizations` - список организаций с фильтрами.
- `POST /api/organizations` - создание организации.
- `GET /api/organizations/filters` - значения фильтров.
- `GET /api/organizations/{organization_id}` - карточка организации.
- `PATCH /api/organizations/{organization_id}` - обновление организации.
- `GET /api/organizations/{organization_id}/risk` - последний прогноз риска.
- `GET /api/organizations/{organization_id}/risk-history` - история прогнозов.

Risk feature snapshots:

- `GET /api/organizations/{organization_id}/feature-snapshots`
- `POST /api/organizations/{organization_id}/feature-snapshots`

ML:

- `GET /api/ml/model-info` - информация о текущей ML-модели из artifact.
- `POST /api/ml/predict/{organization_id}` - prediction по последнему snapshot организации.
- `POST /api/ml/predict-snapshot/{snapshot_id}` - prediction по конкретному snapshot.

Deals:

- `GET /api/organizations/{organization_id}/deals`
- `POST /api/organizations/{organization_id}/deals`
- `PATCH /api/deals/{deal_id}`

Interactions:

- `GET /api/organizations/{organization_id}/interactions`
- `POST /api/organizations/{organization_id}/interactions`
- `PATCH /api/interactions/{interaction_id}`

Reports:

- `GET /api/reports`
- `POST /api/reports`
- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/data`

Other:

- `GET /api/dashboard/summary`
- `GET /api/risk-predictions`
- `GET /api/audit-logs`

Все routes, кроме auth, подключены как protected через dependency `get_current_user`.

## 6. Frontend-страницы и компоненты

Frontend находится в `web/`. Входная точка: `web/src/main.tsx`. Главная оболочка и навигация: `web/src/App.tsx`. Сейчас используется внутреннее состояние страницы, без React Router.

Основные страницы:

- `LoginPage` - вход через Basic Auth.
- `DashboardPage` - сводка по организациям, рискам, сделкам, audit.
- `OrganizationsPage` - список, фильтры, создание организаций.
- `OrganizationDetailPage` - карточка организации, редактирование, snapshots, prediction, risk history, deals.
- `InteractionsPage` - взаимодействия с организациями.
- `ReportsPage` - отчеты и просмотр данных отчета.
- `AuditLogsPage` - audit log.
- `MLModelPage` - информация о ML-модели.
- `RiskExplanationPage` - объяснение факторов риска.

Важные компоненты:

- `features/Deals.tsx`
- `features/ml/MLModelPage.tsx`
- `features/ml/MLModelInfoCard.tsx`
- `features/risk-explanation/*`
- `features/reports/*`
- `features/audit/*`
- `features/interactions/*`

Frontend API client: `web/src/api/client.ts`. API base URL берется из `VITE_API_BASE_URL`, по умолчанию `http://localhost:8000`.

## 7. Таблицы и модели БД

ORM-модели находятся в `app/models/`.

Основные таблицы:

- `roles` - роли пользователей.
- `users` - пользователи, email, хеш пароля, активность, роль.
- `organizations` - организации: БИН, название, отрасль, регион, сегмент, статус, выручка, сотрудники.
- `organization_contacts` - контакты организаций.
- `deals` - сделки с организациями.
- `interactions` - звонки, письма, встречи, заметки, задачи.
- `external_data_sources` - внешние источники.
- `data_import_batches` - партии импорта.
- `risk_feature_snapshots` - входные признаки риска по организации за период.
- `ml_models` - метаданные ML-моделей.
- `risk_predictions` - сохраненные прогнозы риска.
- `reports` - отчеты.
- `audit_logs` - журнал действий.

Миграции лежат в `alembic/versions/`. Структуру БД без необходимости не менять.

## 8. ML-модуль и prediction

ML-код находится в `app/ml/`.

Основные файлы:

- `app/ml/prepare_datasets_from_csv.py` - готовит train/validation датасеты из CSV.
- `app/ml/train_model.py` - обучает модель на подготовленных датасетах.
- `app/ml/predictor.py` - загружает artifact и выполняет prediction по `RiskFeatureSnapshot`.

Artifact модели:

- `artifacts/risk_model.joblib`

Дополнительные артефакты обучения:

- `artifacts/training_report.json`
- `artifacts/training_report.md`
- `artifacts/validation_predictions.csv`

Prediction вызывается через:

- `POST /api/ml/predict/{organization_id}`
- `POST /api/ml/predict-snapshot/{snapshot_id}`

`predictor.py` берет snapshot, рассчитывает признаки, вызывает `model.predict_proba()`, затем комбинирует ML probability с доменной оценкой риска. Итоговый score переводится в `RiskLevel`.

Пороги risk level:

- `< 0.25` - `low`
- `0.25 - 0.55` - `medium`
- `0.55 - 0.80` - `high`
- `>= 0.80` - `critical`

## 9. Docker Compose

Файл: `docker-compose.yml`.

Сервисы:

- `db` - PostgreSQL 16 Alpine.
- `app` - FastAPI backend на порту `8000`.
- `web` - Vite React frontend на порту `5173`.

Запуск:

```bash
docker compose up -d --build
```

Основные Makefile-команды:

```bash
make up
make down
make migrate
make seed
make prepare-datasets
make train
make train-report
make init
```

Прямые Docker-команды для ML:

```bash
docker compose run --rm --no-deps app python -m app.ml.prepare_datasets_from_csv
docker compose run --rm --no-deps app python -m app.ml.train_model
```

Не вставлять реальные значения `.env`, пароли, токены и приватные ключи в ответы или документацию.

## 10. Известные проблемы и незавершенные части

- В проекте есть русские строки с битой кодировкой в части файлов и отчетов.
- В `docker-compose.yml` есть demo-значения для PostgreSQL; лучше вынести чувствительные значения в env.
- Авторизация сейчас Basic Auth, без JWT/session/refresh и без полноценной RBAC-логики.
- Frontend не использует URL routing, поэтому нет прямых ссылок на страницы.
- Отчеты формируются как JSON/data view; генерации PDF/Excel нет.
- Импорт внешних данных представлен моделями, но полноценный pipeline импорта не развит.
- Качество ML-модели умеренное; recall по рисковому классу пока невысокий.
- Текущий CSV в `data/raw/risk_dataset.csv` имеет bankruptcy-формат, поэтому `prepare_datasets_from_csv.py` конвертирует его в CRM-признаки через эвристики.

## 11. Что учитывать при доработке

- Не коммитить `.env`, пароли, токены, приватные ключи и персональные данные.
- При изменении моделей БД создавать/обновлять Alembic migration.
- При изменении ML-признаков синхронно менять:
  - `prepare_datasets_from_csv.py`
  - `train_model.py`
  - `predictor.py`
  - frontend-формы snapshots
  - schemas/models, если меняется контракт данных
- Prediction зависит от наличия `artifacts/risk_model.joblib`.
- `validation_dataset.csv` нельзя использовать для обучения или подбора модели, только для финальной оценки.
- Для validation пропуски должны заполняться медианами, рассчитанными только на train dataset.
- Новые write endpoints желательно логировать через `audit_logs`.

## 12. Главное про обучение модели

Сейчас модель больше не обучается на синтетических данных внутри `train_model.py`. Обучение идет через отдельный ML-пайплайн:

1. Исходный CSV:

```text
data/raw/risk_dataset.csv
```

2. Подготовка датасетов:

```bash
make prepare-datasets
```

Скрипт `app/ml/prepare_datasets_from_csv.py`:

- читает CSV через pandas;
- если CSV уже содержит CRM-колонки, использует их;
- если CSV имеет bankruptcy-формат с `Bankrupt?`, конвертирует финансовые признаки в CRM-риск-признаки;
- проверяет обязательные колонки;
- удаляет строки без target;
- приводит числовые колонки;
- заполняет пропуски медианами;
- проверяет `target` на классы `0` и `1`;
- делает стратифицированное разделение;
- сохраняет:
  - `data/train_dataset.csv` - 500 строк;
  - `data/validation_dataset.csv` - 300 строк.

3. Обучение:

```bash
make train
```

Скрипт `app/ml/train_model.py`:

- читает только `data/train_dataset.csv` для обучения;
- читает `data/validation_dataset.csv` только для проверки;
- проверяет наличие всех feature columns и `target`;
- приводит признаки к числам;
- считает медианы только на train dataset;
- заполняет validation пропуски train-медианами, чтобы не было data leakage;
- обучает `GradientBoostingClassifier`;
- калибрует вероятности через `CalibratedClassifierCV(method="isotonic", cv=3)`;
- выбирает binary classification threshold на train dataset;
- считает validation metrics только на validation dataset.

Feature columns:

```text
log_revenue
log_debt_amount
debt_ratio
overdue_days_30
overdue_days_90
disputes_count
transactions_count
employees_count
low_transactions_flag
```

Target:

```text
target
```

Текущий artifact:

```text
artifacts/risk_model.joblib
```

Artifact сохраняется как словарь:

- `model`
- `feature_columns`
- `target_column`
- `train_medians`
- `classification_threshold`
- `metrics`
- `model_name`
- `version`
- `algorithm_name`
- `trained_at`
- пути к train/validation/report

Текущая версия модели:

```text
gradient_boosting_risk_model
version: 1.2.0
algorithm: GradientBoostingClassifier + IsotonicCalibration
```

Последний результат обучения на validation dataset:

```text
train rows: 500
validation rows: 300
train target distribution: {0: 389, 1: 111}
validation target distribution: {0: 233, 1: 67}

roc_auc: 0.7371
pr_auc: 0.4045
f1: 0.3871
precision: 0.4211
recall: 0.3582
accuracy: 0.7467
brier_score: 0.1556
classification_threshold: 0.402299
confusion_matrix: [[200, 33], [43, 24]]
```

Файлы, которые можно показывать комиссии:

```text
data/train_dataset.csv
data/validation_dataset.csv
artifacts/risk_model.joblib
artifacts/training_report.json
artifacts/training_report.md
artifacts/validation_predictions.csv
docs/ML_TRAINING.md
```

Главное доказательство корректности обучения: модель обучалась на `train_dataset.csv`, качество проверялось на отдельном `validation_dataset.csv`, а validation predictions и training report сохранены отдельными файлами.
