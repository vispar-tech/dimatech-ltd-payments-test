"""Webhook signature helpers for the external payment system."""

import hashlib
from decimal import Decimal
from uuid import UUID


def _format_signature_value(value: int | Decimal | UUID) -> str:
    """Format a webhook field value for signature concatenation."""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        normalized = value.normalize()
        if normalized == normalized.to_integral_value():
            return str(int(normalized))
        text = format(normalized, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    return str(value)


def build_webhook_signature(
    *,
    account_id: int,
    amount: Decimal,
    transaction_id: UUID,
    user_id: int,
    secret_key: str,
) -> str:
    """
    Build SHA256 signature for webhook payload fields (alphabetical key order).

    Concatenation: account_id + amount + transaction_id + user_id + secret_key.
    """
    payload = "".join(
        (
            _format_signature_value(account_id),
            _format_signature_value(amount),
            _format_signature_value(transaction_id),
            _format_signature_value(user_id),
            secret_key,
        )
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_webhook_signature(  # noqa: PLR0913
    *,
    account_id: int,
    amount: Decimal,
    transaction_id: UUID,
    user_id: int,
    signature: str,
    secret_key: str,
) -> bool:
    """Return True when the provided signature matches the expected hash."""
    expected = build_webhook_signature(
        account_id=account_id,
        amount=amount,
        transaction_id=transaction_id,
        user_id=user_id,
        secret_key=secret_key,
    )
    return expected == signature.lower()
