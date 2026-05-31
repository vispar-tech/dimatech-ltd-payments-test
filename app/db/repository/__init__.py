"""Repository layer package providing CRUD abstractions."""

from collections.abc import Sequence
from typing import Any, TypeVar

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import ColumnExpressionArgument, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository[T: Base]:
    """Base repository providing generic CRUD operations for SQLAlchemy models."""

    model: type[T]
    primary_key: str = "id"

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an AsyncSession instance."""
        self.session = session
        if not hasattr(self, "model"):
            raise NotImplementedError("Repository must define a model")

    async def refresh(self, instance: T, attribute_names: list[str] | None = None) -> T:
        """Refresh DB instance attributes from the database."""
        await self.session.flush()
        await self.session.refresh(instance, attribute_names)
        return instance

    async def exists(self, *whereclauses: ColumnExpressionArgument[bool]) -> bool:
        """Check if any record exists."""
        q = select(func.exists().where(*whereclauses))
        res = await self.session.execute(q)
        return bool(res.scalar_one())

    async def add(self, **values: Any) -> T:
        """Create and add a new record."""
        inst = self.model(**values)
        self.session.add(inst)
        return inst

    async def find_one_or_none_by_id(
        self, data_id: int, options: list[ExecutableOption] | None = None
    ) -> T | None:
        """Fetch one record by id or None."""
        q = select(self.model).filter_by(**{self.primary_key: data_id})
        if options:
            q = q.options(*options)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def find_one_or_none(
        self, options: list[ExecutableOption] | None = None, **filter_by: Any
    ) -> T | None:
        """Fetch one record by filters or None."""
        q = select(self.model).filter_by(**filter_by)
        if options:
            q = q.options(*options)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def find_all(
        self,
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
        **filter_by: Any,
    ) -> Sequence[T]:
        """Fetch all records matching filters."""
        q = select(self.model).filter_by(**filter_by)
        if options:
            q = q.options(*options)
        if order_by:
            q = q.order_by(*order_by)
        res = await self.session.execute(q)
        return res.scalars().all()

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
        query = select(self.model)
        if whereclauses:
            query = query.where(*whereclauses)
        if options:
            query = query.options(*options)
        if order_by:
            query = query.order_by(*order_by)

        return await paginate(self.session, query)

    async def find_all_where(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[T]:
        """Fetch all records with where clauses and options."""
        query = select(self.model).where(*whereclauses)
        if options:
            query = query.options(*options)
        if order_by:
            query = query.order_by(*order_by)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, item_id: int, **update_data: Any) -> T | None:
        """Update record by id and return it."""
        stmt = (
            update(self.model)
            .where(getattr(self.model, self.primary_key) == item_id)
            .values(**update_data)
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_where(
        self, *whereclauses: ColumnExpressionArgument[bool], **update_data: Any
    ) -> Sequence[T]:
        """Update multiple records and return them."""
        res = await self.session.execute(
            update(self.model)
            .where(*whereclauses)
            .values(**update_data)
            .returning(self.model)
        )
        return res.scalars().all()

    async def update_by_model(self, instance: T, **update_data: Any) -> T:
        """Update fields of existing model instance."""
        for k, v in update_data.items():
            setattr(instance, k, v)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, item_id: int) -> None:
        """Delete record by id."""
        await self.session.execute(
            delete(self.model).where(getattr(self.model, self.primary_key) == item_id)
        )

    async def delete_where(self, *whereclauses: ColumnExpressionArgument[bool]) -> None:
        """Delete records matching where clauses."""
        await self.session.execute(delete(self.model).where(*whereclauses))
