#!/bin/sh

export COMPOSE_FILE=compose.yml:compose.local.yml

docker compose up db --build