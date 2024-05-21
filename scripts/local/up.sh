#!/bin/sh -x

export COMPOSE_FILE=compose.yml:compose.local.yml

docker compose up --build