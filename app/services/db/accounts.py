from decimal import Decimal
from typing import Any

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.base import ExecutableOption

from app.db.models.accounts import Account
from app.db.repository.accounts import AccountsRepository
from app.services.db import BaseService


class AccountsService(
    BaseService[Account, AccountsRepository],
):
    """Database service for Account persistence."""

    repository_class = AccountsRepository

    async def find_paginated(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """Retrieve paginated results for accounts, defaulting to id DESC."""
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
        """Retrieve paginated accounts filtered by user_id."""
        return await self.find_paginated(
            self.repository.model.user_id == user_id,
            options=options,
            order_by=order_by,
        )

    async def create_with_id(
        self,
        account_id: int,
        user_id: int,
        balance: Decimal = Decimal("0.00"),
    ) -> Account:
        """Create an account with an explicit primary key."""
        account = await self.add(id=account_id, user_id=user_id, balance=balance)
        await self.repository.session.flush()
        return account

    async def create_with_id_safe(
        self,
        account_id: int,
        user_id: int,
        balance: Decimal = Decimal("0.00"),
    ) -> Account:
        """
        Create an account or return the existing row after a concurrent insert.

        Uses a savepoint so IntegrityError does not abort the outer transaction.
        """
        session = self.repository.session
        try:
            async with session.begin_nested():
                return await self.create_with_id(account_id, user_id, balance)
        except IntegrityError:
            account = await self.find_one_or_none_by_id(account_id)
            if account is None:
                raise
            return account

    async def credit_balance(self, account: Account, amount: Decimal) -> Account:
        """Increase account balance and flush changes."""
        account.balance += amount
        await self.repository.session.flush()
        return await self.refresh(account)
