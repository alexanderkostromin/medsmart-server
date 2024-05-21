# syntax=docker/dockerfile:1

# set up shared environment variables
FROM python:3.12.2-slim as python-base

ENV \ 
    # python
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    # paths
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:/$VENV_PATH/bin:$PATH"



# build deps and create virtual environment
FROM python-base as builder-base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    # poetry deps
    curl \
    # python deps build deps
    build-essential

RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

WORKDIR "$PYSETUP_PATH"
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache \
    poetry install --without=dev



# image for development / testing
FROM python-base as development
ENV FASTAPI_ENV=development
WORKDIR "$PYSETUP_PATH"

COPY --from=builder-base "$POETRY_HOME" "$POETRY_HOME"
COPY --from=builder-base "$PYSETUP_PATH" "$PYSETUP_PATH"

RUN --mount=type=cache,target=/root/.cache \
    poetry install --with=dev

WORKDIR /app

COPY ./src ./src

CMD [ \
    "uvicorn", \
    "--host", "0.0.0.0", "--port", "8080", \
    "--log-config", "src/log-config.json", \
    "--reload", \
    "--factory",  \
    "--app-dir", "src", \
    "app:create_app"\
    ]



# image for production
FROM python-base as production
ENV FASTAPI_ENV=production

COPY --from=builder-base "$PYSETUP_PATH" "$PYSETUP_PATH"

WORKDIR /app

COPY ./src ./src

CMD [ \
    "gunicorn", \
    "--config", "src/gunicorn.conf.py", \
    "app:create_app()" \
    ]