from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.models.users import User
from app.services.auth.dependencies import get_current_admin_user, get_current_user
from app.services.db.accounts import AccountsService
from app.services.db.payments import PaymentsService
from app.services.db.users import UsersService
from app.web.api.v1.accounts.schemas import AccountRead
from app.web.api.v1.payments.schemas import PaymentRead
from app.web.schemas import Paginated

router = APIRouter(prefix="/accounts")


@router.get(
    "/own",
    response_model=Paginated[AccountRead],
    summary="Get accounts owned by the authenticated user",
    operation_id="get_own_accounts",
)
async def get_own_accounts(
    current_user: User = Depends(get_current_user),
    accounts_service: AccountsService = Depends(),
) -> Paginated[AccountRead]:
    """Get a list of accounts and balances owned by the authenticated user."""
    return await accounts_service.find_paginated_for_user(current_user.id)


@router.get(
    "/",
    response_model=Paginated[AccountRead],
    summary="Get accounts by userId (admin only)",
    operation_id="get_accounts_by_userid",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_accounts_admin(
    user_id: int | None = Query(
        default=None,
        description="Filter by user id (required for admins)",
        alias="userId",
    ),
    accounts_service: AccountsService = Depends(),
    users_service: UsersService = Depends(),
) -> Paginated[AccountRead]:
    """
    Admin only: Get a list of accounts and balances for a specific user.

    Must specify user_id to query accounts for a specific user.
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

    return await accounts_service.find_paginated_for_user(user_id)


@router.get(
    "/{account_id}/payments",
    response_model=Paginated[PaymentRead],
    summary="Get payments for given account_id (admin can query any, user only own)",
    operation_id="get_payments_by_account_id",
)
async def get_payments_by_account_id(
    account_id: int,
    payments_service: PaymentsService = Depends(),
    accounts_service: AccountsService = Depends(),
    current_user: User = Depends(get_current_user),
) -> Paginated[PaymentRead]:
    """
    Get all payments for given account_id.

    If called by admin, any account_id can be accessed.
    If called by normal user, only own accounts can be accessed.
    """
    account = await accounts_service.find_one_or_none_by_id(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    # Normal user: can only query own accounts
    if not current_user.is_admin and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted to access payments for this account",
        )

    # Either admin or owner: return payments
    return await payments_service.find_paginated_for_account(account_id)
