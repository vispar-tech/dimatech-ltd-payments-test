from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.models.users import User
from app.services.auth.dependencies import get_current_admin_user, get_current_user
from app.services.db.payments import PaymentsService
from app.services.db.users import UsersService
from app.services.payments.exceptions import (
    InvalidWebhookSignatureError,
    PaymentWebhookError,
    WebhookAccountOwnershipError,
    WebhookUserNotFoundError,
)
from app.services.payments.service import PaymentService, get_payment_service
from app.services.payments.types import PaymentWebhookPayload
from app.web.api.v1.payments.schemas import (
    PaymentRead,
    PaymentWebhookRequest,
    PaymentWebhookResponse,
)
from app.web.schemas import Paginated

router = APIRouter(prefix="/payments")


@router.post(
    "/webhook",
    response_model=PaymentWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Process payment webhook from external system",
    operation_id="process_payment_webhook",
)
async def process_payment_webhook(
    payload: PaymentWebhookRequest,
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentWebhookResponse:
    """Emulate webhook handling from an external payment provider."""
    try:
        result = await payment_service.process_webhook(
            PaymentWebhookPayload(
                transaction_id=payload.transaction_id,
                user_id=payload.user_id,
                account_id=payload.account_id,
                amount=payload.amount,
                signature=payload.signature,
            )
        )
    except InvalidWebhookSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc
    except WebhookUserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
    except WebhookAccountOwnershipError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc
    except PaymentWebhookError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc

    return PaymentWebhookResponse(
        payment=PaymentRead.model_validate(result.payment, from_attributes=True),
        already_processed=result.already_processed,
    )


@router.get(
    "/own",
    response_model=Paginated[PaymentRead],
    summary="Get payments owned by the authenticated user",
    operation_id="get_own_payments",
)
async def get_own_payments(
    current_user: User = Depends(get_current_user),
    payments_service: PaymentsService = Depends(),
) -> Paginated[PaymentRead]:
    """Get a list of payments owned by the authenticated user."""
    return await payments_service.find_paginated_for_user(current_user.id)


@router.get(
    "/",
    response_model=Paginated[PaymentRead],
    summary="Get payments by userId (admin only)",
    operation_id="get_payments_by_userid",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_payments_admin(
    user_id: int | None = Query(
        default=None,
        description="Filter by user id (required for admins)",
        alias="userId",
    ),
    payments_service: PaymentsService = Depends(),
    users_service: UsersService = Depends(),
) -> Paginated[PaymentRead]:
    """
    Admin only: Get a list of payments for a specific user.

    Must specify user_id to query payments for a specific user.
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Admin users must specify userId parameter.",
        )

    user = await users_service.find_one_or_none_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await payments_service.find_paginated_for_user(user_id)
