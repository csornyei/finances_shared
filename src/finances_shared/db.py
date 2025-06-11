from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from finances_shared.params import DatabaseParams

_engine = None
_async_session = None


def init_db(logger: Logger):
    global _engine, _async_session
    db_params = DatabaseParams.from_env(logger)
    if _engine is None:
        _engine = create_async_engine(
            db_params.connection_string(), echo=True, future=True
        )
    if _async_session is None:
        _async_session = sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


# Dependency for route handlers
async def get_db():
    if _async_session is None:
        raise RuntimeError("Database session is not initialized. Call init_db() first.")
    async with _async_session() as session:
        yield session
