#!/bin/sh

export COMPOSE_FILE=compose.yml:compose.local.yml

docker compose restart server