"""Business logic for payment processing."""

from fastapi import Depends

from app.db.models.accounts import Account
from app.services.db.accounts import AccountsService
from app.services.db.payments import PaymentsService
from app.services.db.users import UsersService
from app.services.payments.exceptions import (
    InvalidWebhookSignatureError,
    WebhookAccountOwnershipError,
    WebhookUserNotFoundError,
)
from app.services.payments.signature import verify_webhook_signature
from app.services.payments.types import PaymentWebhookPayload, PaymentWebhookResult
from app.settings import settings


class PaymentService:
    """Application service for payment workflows."""

    def __init__(
        self,
        payments_db: PaymentsService,
        accounts_db: AccountsService,
        users_db: UsersService,
    ) -> None:
        """Wire database services used by payment use cases."""
        self._payments_db = payments_db
        self._accounts_db = accounts_db
        self._users_db = users_db

    def _ensure_account_belongs_to_user(self, account: Account, user_id: int) -> None:
        if account.user_id != user_id:
            raise WebhookAccountOwnershipError(
                "Account does not belong to the specified user"
            )

    async def _get_or_create_account(
        self,
        *,
        account_id: int,
        user_id: int,
    ) -> Account:
        """Return the user's account, creating it when missing."""
        account = await self._accounts_db.find_one_or_none_by_id(account_id)
        if account is not None:
            self._ensure_account_belongs_to_user(account, user_id)
            return account

        account = await self._accounts_db.create_with_id_safe(
            account_id=account_id,
            user_id=user_id,
        )
        self._ensure_account_belongs_to_user(account, user_id)
        return account

    async def process_webhook(
        self,
        payload: PaymentWebhookPayload,
    ) -> PaymentWebhookResult:
        """
        Process an external payment webhook.

        Verifies signature, ensures account exists, records payment once,
        and credits the account balance.

        Raises:
            InvalidWebhookSignatureError: Signature verification failed.
            WebhookUserNotFoundError: User id is unknown.
            WebhookAccountOwnershipError: Account belongs to another user.
        """
        if not verify_webhook_signature(
            account_id=payload.account_id,
            amount=payload.amount,
            transaction_id=payload.transaction_id,
            user_id=payload.user_id,
            signature=payload.signature,
            secret_key=settings.payments_secret_key,
        ):
            raise InvalidWebhookSignatureError("Invalid webhook signature")

        existing = await self._payments_db.find_by_transaction_id(
            payload.transaction_id
        )
        if existing is not None:
            return PaymentWebhookResult(payment=existing, already_processed=True)

        user = await self._users_db.find_one_or_none_by_id(payload.user_id)
        if user is None:
            raise WebhookUserNotFoundError("User not found")

        account = await self._get_or_create_account(
            account_id=payload.account_id,
            user_id=payload.user_id,
        )

        payment = await self._payments_db.create_payment(
            transaction_id=payload.transaction_id,
            user_id=payload.user_id,
            account_id=payload.account_id,
            amount=payload.amount,
        )
        await self._accounts_db.credit_balance(account, payload.amount)

        return PaymentWebhookResult(payment=payment, already_processed=False)


def get_payment_service(
    payments_db: PaymentsService = Depends(),
    accounts_db: AccountsService = Depends(),
    users_db: UsersService = Depends(),
) -> PaymentService:
    """Dependency injector for PaymentService."""
    return PaymentService(
        payments_db=payments_db,
        accounts_db=accounts_db,
        users_db=users_db,
    )
