from fastapi import APIRouter, Depends, HTTPException, status

from app.db.models.users import User
from app.services.auth.dependencies import get_current_admin_user, get_current_user
from app.services.db.users import UsersService
from app.web.api.v1.users.schemas import UserCreate, UserRead, UserUpdate
from app.web.schemas import Paginated

router = APIRouter(prefix="/users")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current authenticated user",
    operation_id="get_current_user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated user's details."""
    return current_user


@router.get(
    "/",
    response_model=Paginated[UserRead],
    summary="List all users",
    operation_id="list_users",
    dependencies=[Depends(get_current_admin_user)],
)
async def list_users(users_service: UsersService = Depends()) -> Paginated[UserRead]:
    """Retrieve a paginated list of all users (admin only)."""
    return await users_service.find_paginated()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    operation_id="create_user",
    dependencies=[Depends(get_current_admin_user)],
)
async def create_user(
    user: UserCreate, users_service: UsersService = Depends()
) -> User:
    """Create a new user and return their data (admin only)."""
    is_user_exists = await users_service.exists_by_email(user.email)
    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    new_user = await users_service.add(**user.model_dump())
    return await users_service.refresh(new_user, attribute_names=["id"])


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by ID",
    operation_id="get_user_by_id",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_user(user_id: int, users_service: UsersService = Depends()) -> User:
    """Get details of a user by their ID (admin only)."""
    db_user = await users_service.find_one_or_none_by_id(user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    operation_id="update_user",
    dependencies=[Depends(get_current_admin_user)],
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    users_service: UsersService = Depends(),
) -> User:
    """Update a user's details (admin only)."""
    update_data = user_update.model_dump(exclude_unset=True)
    db_user = await users_service.update(user_id, **update_data)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a user",
    operation_id="delete_user",
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_user(
    user_id: int,
    users_service: UsersService = Depends(),
) -> None:
    """Delete a user by ID (admin only)."""
    db_user = await users_service.find_one_or_none_by_id(user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await users_service.delete(user_id)
