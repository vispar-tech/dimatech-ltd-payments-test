from typing import Any

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.sql.base import ExecutableOption

from app.db.models.users import User
from app.db.repository.users import UsersRepository
from app.services.db import BaseService


class UsersService(
    BaseService[User, UsersRepository],
):
    """Service for User model."""

    repository_class = UsersRepository

    async def find_paginated(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """Retrieve paginated results for users, defaulting to created_at DESC."""
        if order_by is None:
            order_by = [User.created_at.desc()]
        return await self.repository.find_paginated(
            *whereclauses, options=options, order_by=order_by
        )

    async def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the specified email."""
        return await self.exists(self.repository.model.email == email)

    async def find_one_by_email(self, email: str) -> User | None:
        """Find a user by email."""
        return await self.repository.find_one_or_none(email=email)
