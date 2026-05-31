from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.models.users import User
from app.services.auth.dependencies import get_current_admin_user, get_current_user
from app.services.db.payments import PaymentsService
from app.services.db.users import UsersService
from app.web.api.v1.payments.schemas import PaymentRead
from app.web.schemas import Paginated

router = APIRouter(prefix="/payments")


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
