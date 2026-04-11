SERVER_DIR=apps/server
CLIENT_DIR=apps/client

OPENAPI_URL=http://localhost:8000/openapi.json

install-backend:
	poetry -C $(SERVER_DIR) install

run-backend:
	poetry -C $(SERVER_DIR) run uvicorn app.main:app --reload

test-backend:
	poetry -C $(SERVER_DIR) run pytest

lint-backend:
	poetry -C $(SERVER_DIR) run ruff check .

format-backend:
	poetry -C $(SERVER_DIR) run black .
	poetry -C $(SERVER_DIR) run isort .


install-frontend:
	cd $(CLIENT_DIR) && npm install

run-frontend:
	cd $(CLIENT_DIR) && npm run dev

build-frontend:
	cd $(CLIENT_DIR) && npm run build

openapi-gen:
	cd $(CLIENT_DIR) && npx openapi-typescript $(OPENAPI_URL) -o src/api/schema.d.ts


setup:
	make install-backend
	make install-frontend

dev-backend:
	make run-backend

dev-frontend:
	make run-frontend

dev:
	make -j 2 run-backend run-frontend


gen-api:
	make run-backend & sleep 5 && make openapi-gen


clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf apps/client/.next
	rm -rf apps/server/.pytest_cache

# currently being used
# be
run-be:
	poetry -C $(SERVER_DIR) run uvicorn src.api.main:app --reload

fmt-be:
	poetry -C $(SERVER_DIR) run black . --line-length 79
	poetry -C $(SERVER_DIR) run isort .

lint-be:
	poetry -C $(SERVER_DIR) run pycodestyle src
	poetry -C $(SERVER_DIR) run pylint src


# fe
run-fe:
	cd $(CLIENT_DIR) && pnpm run dev

build-fe:
	cd $(CLIENT_DIR) && pnpm run build