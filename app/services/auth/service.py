import logging

from fastapi import Depends, HTTPException, status

from app.db.models.users import User
from app.services.auth.helpers import PasswordHelper
from app.services.auth.tokens import TokenService
from app.services.db.users import UsersService
from app.web.responses import ORJSONResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self, users_service: UsersService = Depends()) -> None:
        """Init AuthService with UsersService."""
        self._users_service = users_service
        self.password_helper = PasswordHelper()

    async def login(self, email: str, password: str) -> ORJSONResponse:
        """Authenticate user and set auth cookies."""
        user = await self._users_service.find_one_by_email(email=email)
        if user is None:
            logger.debug(f"Login failed for email: {email}")
            # Run the hasher to mitigate timing attack
            self.password_helper.hash(password)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        verified, updated_password_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not verified:
            logger.debug(f"Login failed for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if updated_password_hash is not None:
            await self._users_service.update_by_model(
                user, hashed_password=updated_password_hash
            )

        user_id = user.id
        access_token = TokenService.encode_token(user_id)
        refresh_token = TokenService.encode_refresh_token(user_id)

        response = ORJSONResponse(
            content={"accessToken": access_token, "refreshToken": refresh_token}
        )
        TokenService.set_auth_cookies(response, access_token, refresh_token)

        logger.debug(f"User {email} logged in successfully")
        return response

    def logout(self) -> ORJSONResponse:
        """Clear authentication cookies."""
        response = ORJSONResponse(content={})
        TokenService.clear_auth_cookies(response)
        logger.debug("User logged out")
        return response

    async def get_by_email(self, email: str) -> User:
        """Retrieve a user by email, or raise HTTP 404 if not found."""
        user = await self._users_service.find_one_by_email(email=email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def refresh(
        self,
        refresh_token: str | None,
    ) -> ORJSONResponse:
        """Refresh access and refresh tokens."""
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token provided",
            )

        user_id = TokenService.decode_refresh_token(refresh_token)
        user = await self._users_service.find_one_or_none_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        user_id = user.id
        access_token = TokenService.encode_token(user_id)
        refresh_token = TokenService.encode_refresh_token(user_id)

        response = ORJSONResponse(
            content={"accessToken": access_token, "refreshToken": refresh_token}
        )
        TokenService.set_auth_cookies(response, access_token, refresh_token)

        logger.debug(f"User {user.email} refresh tokens in successfully")
        return response


def get_auth_service(users_service: UsersService = Depends()) -> AuthService:
    """Dependency injector for AuthService."""
    return AuthService(users_service=users_service)
