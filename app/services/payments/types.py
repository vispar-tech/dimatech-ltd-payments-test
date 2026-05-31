"""Data types for payment webhook processing."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.db.models.payments import Payment


@dataclass(frozen=True, slots=True)
class PaymentWebhookPayload:
    """Normalized webhook payload from an external payment system."""

    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal
    signature: str


@dataclass(slots=True)
class PaymentWebhookResult:
    """Result of a successful webhook processing attempt."""

    payment: Payment
    already_processed: bool
