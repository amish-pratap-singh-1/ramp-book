SERVER_DIR=apps/server
CLIENT_DIR=apps/client

OPENAPI_URL=http://localhost:8000/openapi.json

# generate contract
gen-ts:
	cd $(CLIENT_DIR) && pnpm openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts
# be
run-be:
	poetry -C $(SERVER_DIR) run uvicorn src.api.main:app --reload

fmt-be:
	poetry -C $(SERVER_DIR) run black . --line-length 79
	poetry -C $(SERVER_DIR) run isort .

lint-be:
	poetry -C $(SERVER_DIR) run pycodestyle src
	poetry -C $(SERVER_DIR) run pylint --disable=R0903,R0801 src

gen-migration:
	poetry -C $(SERVER_DIR) run alembic revision --autogenerate -m "auto"

apply-migration:
	poetry -C $(SERVER_DIR) run alembic upgrade head

seed-be:
	poetry -C $(SERVER_DIR) run python scripts/seed.py



# fe
run-fe:
	cd $(CLIENT_DIR) && pnpm run dev

build-fe:
	cd $(CLIENT_DIR) && pnpm run build

# db

# project
run-project:
	# Setup db
	docker compose up --build -d postgres

	# Wait for DB using container
	until docker compose exec postgres pg_isready -U postgres; do \
		echo "Waiting for Postgres..."; \
		sleep 2; \
	done

	# Setup python
	poetry -C $(SERVER_DIR) install

	# Run Migration on db
	poetry -C $(SERVER_DIR) run alembic upgrade head

	# Seed data on db
	poetry -C $(SERVER_DIR) run python scripts/seed.py

	# Run backend
	docker compose up --build -d server

	# Run client
	docker compose up --build -d client



dev-project:
	dev commands