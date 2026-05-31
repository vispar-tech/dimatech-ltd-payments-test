from typing import Any

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.sql.base import ExecutableOption

from app.db.models.accounts import Account
from app.db.repository.accounts import AccountsRepository
from app.services.db import BaseService


class AccountsService(
    BaseService[Account, AccountsRepository],
):
    """Service for Account model."""

    repository_class = AccountsRepository

    async def find_paginated(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """Retrieve paginated results for accounts, defaulting to created_at DESC."""
        if order_by is None:
            order_by = [Account.id.desc()]
        return await self.repository.find_paginated(
            *whereclauses, options=options, order_by=order_by
        )

    async def find_paginated_for_user(
        self,
        user_id: int,
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """Shortcut to retrieve paginated accounts filtered by user_id."""
        return await self.find_paginated(
            self.repository.model.user_id == user_id,
            options=options,
            order_by=order_by,
        )
