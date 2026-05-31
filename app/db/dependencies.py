import logging
from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

logger = logging.getLogger(__name__)


async def get_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session.

    Args:
        request: current request.

    Yields:
        sqlalchemy.ext.asyncio.AsyncSession: database session.
    """
    async with request.app.state.db_session_factory() as session:
        await session.begin()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            logger.error("Database session rollback due to SQLAlchemyError")

            raise
        else:
            await session.commit()
        finally:
            await session.close()
