import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from application.handlers.auth import router as auth_router
from application.handlers.images import router as images_router
from application.handlers.predict import router as predict_router
from application.handlers.users import router as users_router
from config import get_config
from infrastructure.engine import setup_engine, shutdown_engine
from log.setup import setup_logging

# from utils.log import setup_file_handler, setup_stream_handler

# def setup_logging(production: bool, log_file: Path) -> None:
#     if production:
#         log_level = logging.INFO
#     else:
#         log_level = logging.DEBUG
#     logging.root.setLevel(log_level)
#     setup_stream_handler(level=log_level)
#     setup_file_handler(log_file, level=log_level)


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(images_router)
    app.include_router(predict_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    setup_logging(config.log_config_path)
    # setup_logging(config.production, config.log_dir / "med-exam-web-server.log")
    await setup_engine()
    yield
    await shutdown_engine()


def create_app() -> FastAPI:
    config = get_config()
    app = FastAPI(
        title="Medical Exam Web",
        version=config.version,
        root_path=config.web_root_path,
        lifespan=lifespan,
    )
    setup_routers(app)
    return app
