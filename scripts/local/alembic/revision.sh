#!/bin/sh

# DB connection settings - check
export DB_DIALECT=postgresql
export DB_DRIVER=asyncpg
export DB_USERNAME=postgres
export DB_PASSWORD=postgres
export DB_HOST="0.0.0.0"
export DB_NAME=main
export DB_MAX_CONNECTIONS=100

export DB_PORT=54328 # <- check twice

pipenv run alembic revision -m "$1" --autogenerate