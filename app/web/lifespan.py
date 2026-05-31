from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.settings import settings
from app.web.openapi import update_openapi_schema


def _setup_db(app: FastAPI) -> None:
    """Create connection to the database.

    This function creates an SQLAlchemy engine instance and a session factory
    for creating sessions, then stores them in the application's state property.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    """Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    Args:
        app: the fastAPI application.

    Yields:
        None

    Returns:
        function that actually performs actions.
    """
    app.middleware_stack = None
    _setup_db(app)
    update_openapi_schema(app)

    yield

    await app.state.db_engine.dispose()
