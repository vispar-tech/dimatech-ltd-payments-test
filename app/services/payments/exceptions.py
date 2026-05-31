"""Domain exceptions for payment webhook processing."""


class PaymentWebhookError(Exception):
    """Base error for webhook processing failures."""

    def __init__(self, message: str) -> None:
        """Store a human-readable error message."""
        self.message = message
        super().__init__(message)


class InvalidWebhookSignatureError(PaymentWebhookError):
    """Raised when the webhook signature does not match the payload."""


class WebhookUserNotFoundError(PaymentWebhookError):
    """Raised when the referenced user does not exist."""


class WebhookAccountOwnershipError(PaymentWebhookError):
    """Raised when the account belongs to another user."""
