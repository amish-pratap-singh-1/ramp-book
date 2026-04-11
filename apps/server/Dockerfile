FROM python:3.13-slim-bookworm

# 1. Combined ENV vars (Added a version for Poetry)
ENV POETRY_VERSION=2.3.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# 2. Install Poetry once
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# 3. Layer caching for dependencies
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --only main

# 4. Copy application code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]