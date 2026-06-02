up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d --build

logs:
	docker compose logs -f

logs-app:
	docker compose logs app --tail=100 -f

logs-web:
	docker compose logs web --tail=100 -f

logs-db:
	docker compose logs db --tail=100 -f

migrate:
	docker compose run --rm app alembic upgrade head

revision:
	docker compose run --rm app alembic revision --autogenerate -m "change schema"

seed:
	docker compose run --rm app python -m app.scripts.seed

train:
	docker compose run --rm --no-deps app python -m app.ml.train_model

prepare-datasets:
	python -m app.ml.prepare_datasets_from_csv

init:
	docker compose up -d --build
	docker compose run --rm app alembic upgrade head
	docker compose run --rm app python -m app.scripts.seed
	docker compose run --rm --no-deps app python -m app.ml.train_model

ps:
	docker compose ps

db-shell:
	docker compose exec db psql -U risk_user -d risk_crm

check-tables:
	docker compose exec db psql -U risk_user -d risk_crm -c "\dt"

clean:
	docker compose down

clean-volumes:
	docker compose down -v
