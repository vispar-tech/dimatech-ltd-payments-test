from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.web.schemas import CamelCaseModel


class PaymentRead(CamelCaseModel):
    """Read schema for Payment."""

    id: int
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal
    created_at: datetime


class PaymentWebhookRequest(CamelCaseModel):
    """Incoming webhook payload from the external payment system."""

    transaction_id: UUID
    user_id: int = Field(gt=0)
    account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    signature: str = Field(min_length=64, max_length=64)


class PaymentWebhookResponse(CamelCaseModel):
    """Webhook processing result."""

    payment: PaymentRead
    already_processed: bool = False
