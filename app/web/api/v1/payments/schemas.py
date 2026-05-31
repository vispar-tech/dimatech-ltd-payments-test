from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.web.schemas import CamelCaseModel


class PaymentRead(CamelCaseModel):
    """Read schema for Payment."""

    id: int
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal
    created_at: datetime
