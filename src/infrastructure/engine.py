import logging

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from application.dependencies.config import get_config
from infrastructure.entities import Base
from infrastructure.entities.mixins.audit import create_updated_at_triggers

logger = logging.getLogger(__name__)
config = get_config()
engine = create_async_engine(
    url=config.db_url,
    pool_size=config.db_pool_size,
    max_overflow=config.db_max_overflow,
)
async_session = async_sessionmaker(engine)


async def setup_engine():
    async with engine.connect() as conn:
        try:
            await conn.run_sync(create_updated_at_triggers, Base.metadata)
        except exc.SQLAlchemyError as e:
            logger.warning(e)


async def shutdown_engine():
    await engine.dispose()
