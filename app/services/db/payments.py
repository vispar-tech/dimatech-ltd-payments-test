from typing import Any

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.sql.base import ExecutableOption

from app.db.models.payments import Payment
from app.db.repository.payments import PaymentsRepository
from app.services.db import BaseService


class PaymentsService(
    BaseService[Payment, PaymentsRepository],
):
    """Service for Payment model."""

    repository_class = PaymentsRepository

    async def find_paginated(
        self,
        *whereclauses: ColumnExpressionArgument[bool],
        options: list[ExecutableOption] | None = None,
        order_by: list[str | ColumnExpressionArgument[Any]] | None = None,
    ) -> Any:
        """Retrieve paginated results for payments, defaulting to created_at DESC."""
        if order_by is None:
            order_by = [Payment.created_at.desc()]
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
