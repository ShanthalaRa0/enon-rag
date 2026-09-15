#!/bin/bash
set -e

echo "Starting PostgreSQL..."

docker-entrypoint.sh postgres &
POSTGRES_PID=$!

echo "Waiting for PostgreSQL..."

until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    sleep 1
done

echo "PostgreSQL is ready."

echo "Running 001_create_schema.sql..."

psql \
    -v ON_ERROR_STOP=1 \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -f /docker-entrypoint-initdb.d/001_create_schema.sql

echo "Schema initialization completed."

wait $POSTGRES_PID