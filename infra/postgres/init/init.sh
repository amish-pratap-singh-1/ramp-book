#!/bin/bash
set -e

echo "🚀 Starting Postgres initialization..."

# Validate required env vars
if [ -z "$APP_DB" ] || [ -z "$APP_USER" ] || [ -z "$APP_PASSWORD" ]; then
    echo "❌ Missing APP_DB / APP_USER / APP_PASSWORD"
    exit 1
fi


# Create DB + User
psql -v ON_ERROR_STOP=1 \
--username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" <<EOSQL

CREATE DATABASE $APP_DB;

CREATE USER $APP_USER WITH ENCRYPTED PASSWORD '$APP_PASSWORD';

GRANT CONNECT ON DATABASE $APP_DB TO $APP_USER;

EOSQL


# Configure FULL permissions inside app_db
psql -v ON_ERROR_STOP=1 \
--username "$POSTGRES_USER" \
--dbname "$APP_DB" <<EOSQL

-- Remove default restrictions
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- FULL schema access (VERY IMPORTANT)
GRANT USAGE, CREATE ON SCHEMA public TO $APP_USER;

-- Full access to existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $APP_USER;

-- Full access to sequences (SERIAL / IDENTITY support)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $APP_USER;

-- Full access to functions (optional but “full” means include this)
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $APP_USER;

-- Ensure future tables also get full access
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO $APP_USER;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO $APP_USER;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON FUNCTIONS TO $APP_USER;

EOSQL

echo "✅ Postgres initialization completed successfully."