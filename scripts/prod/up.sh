#!/bin/sh -x

export DOCKER_CONTEXT=med-web

docker compose up --build --remove-orphans