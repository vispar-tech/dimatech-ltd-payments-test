import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie

from app.db.models.users import User
from app.services.auth.tokens import TokenService
from app.services.db.users import UsersService

logger = logging.getLogger(__name__)

# FastAPI Security APIKeyCookie dependencies for cookie authentication
access_token_cookie_scheme = APIKeyCookie(name="accessToken", auto_error=False)
refresh_token_cookie_scheme = APIKeyCookie(name="refreshToken", auto_error=False)


def get_access_token_cookie(
    access_token: str | None = Depends(access_token_cookie_scheme),
) -> str | None:
    """Retrieve access token from cookie."""
    return access_token


def get_refresh_token_cookie(
    refresh_token: str | None = Depends(refresh_token_cookie_scheme),
) -> str | None:
    """Retrieve refresh token from cookie."""
    return refresh_token


async def get_current_user_id(
    access_token: str | None = Depends(get_access_token_cookie),
) -> int:
    """Decode token and return current user's ID."""
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    try:
        user_id = TokenService.decode_token(access_token)
    except Exception as err:
        logger.error(f"Failed to decode token: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        ) from err
    return user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    users_service: UsersService = Depends(),
) -> User:
    """Dependency to get the current authenticated user."""
    user = await users_service.find_one_or_none_by_id(data_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def get_current_admin_user(
    user_id: int = Depends(get_current_user_id),
    users_service: UsersService = Depends(),
) -> User:
    """Dependency to get the current authenticated admin user."""
    user = await users_service.find_one_or_none_by_id(data_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin"
        )
    return user
