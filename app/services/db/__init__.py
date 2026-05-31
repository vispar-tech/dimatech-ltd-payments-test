"""Database service layer initialization and base service definition."""

from collections.abc import Sequence
from typing import Any, TypeVar

from fastapi import Depends
from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.db.base import Base
from app.db.dependencies import get_db_session
from app.db.repository import BaseRepository

T = TypeVar("T", bound=Base)
R = TypeVar("R", bound=BaseRepository[Any])


class BaseService[T: Base, R: BaseRepository[Any]]:
    """Base service providing CRUD operations using the new repository layer."""

    repository_class: type[R]

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        """Initialize the service with a repository using the provided session."""
        if not hasattr(self, "repository_class"):
            raise NotImplementedError("Service must define repository_class")
        self.repository = self.repository_class(session)

    async def refresh(
        self,
        instance: T,
        attribute_names: list[str] | None = None,
    ) -> T:
        """Refresh instance attributes from database."""
        return await self.repository.refresh(instance, attribute_names)

    async def exists(self, *whereclauses: ColumnExpressionArgument[bool]) -> bool:
        """Check if any record exists with the given where clauses."""
        return await self.repository.exists(*whereclauses)

    async def add(self, **values: Any) -> T:
        """Create and add new record."""
        return await self.repository.add(**values)

    async def find_one_or_none_by_id(
        self, data_id: int, options: list[ExecutableOption] | None = None
    ) -> T | None:
        """Get record by primary key."""
        return await self.repository.find_one_or_none_by_id(data_id, options=options)

    async def find_one_or_none(
        self, options: list[ExecutableOption] | None = None, **filter_by: Any
    ) -> T | None:
        """Find single record by filters."""
        return await self.repository.find_one_or_none(options=options, **filter_by)

    async def find_all(
        self,
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
        **filter_by: Any,
    ) -> Sequence[T]:
        """Get all records with filters, supports options and order_by."""
        return await self.repository.find_all(
            options=options,
            order_by=order_by,
            **filter_by,
        )

    async def find_paginated(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """
        Retrieve paginated results.

        Args:
            *whereclauses: SQLAlchemy expressions for WHERE clause.
            options: SQLAlchemy loader/load options.
            order_by: List of columns to order by.

        Returns:
            Paginated results.
        """
        return await self.repository.find_paginated(
            *whereclauses, options=options, order_by=order_by
        )

    async def find_all_where(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[T]:
        """Find records with complex where conditions and extra options."""
        return await self.repository.find_all_where(
            *whereclauses,
            options=options,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    async def update(
        self,
        item_id: int,
        **update_data: Any,
    ) -> T | None:
        """Update record by ID."""
        return await self.repository.update(item_id, **update_data)

    async def update_where(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        **update_data: Any,
    ) -> Sequence[T]:
        """Update all records matching conditions."""
        return await self.repository.update_where(*whereclauses, **update_data)

    async def update_by_model(
        self,
        instance: T,
        **update_data: Any,
    ) -> T:
        """Update model instance fields."""
        return await self.repository.update_by_model(instance, **update_data)

    async def delete(self, item_id: int) -> None:
        """Delete record by id."""
        await self.repository.delete(item_id)

    async def delete_where(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
    ) -> None:
        """Delete records matching conditions."""
        await self.repository.delete_where(*whereclauses)
