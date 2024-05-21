#!/bin/sh

# SSH config (omit to use local)
export SSH_HOST=med-web
export SSH_PORT=22
export SSH_USER=root
export SSH_PKEY=/home/vancomm/.ssh/vancomm

# connection settings - check
export DB_DIALECT=postgresql
export DB_DRIVER=asyncpg
export DB_USERNAME=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_NAME=main
export DB_MAX_CONNECTIONS=100

export DB_PORT=54320 # <- check twice

pipenv run alembic upgrade head