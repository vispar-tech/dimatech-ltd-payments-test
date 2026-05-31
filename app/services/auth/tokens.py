from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException

from app.settings import settings
from app.web.responses import ORJSONResponse


class TokenService:
    """Service for encoding/decoding JWT tokens and managing auth cookies."""

    _secret = settings.jwt_users_secret
    _access_cookie_max_age = 15 * 60  # 15 minutes
    _refresh_cookie_max_age = 7 * 24 * 60 * 60  # 7 days

    @classmethod
    def _generate_token(
        cls, user_id: int | str, scope: str, expires_delta: timedelta
    ) -> str:
        """Generate a JWT for a user with given scope and expiry."""
        now = datetime.now(UTC)
        payload = {
            "exp": now + expires_delta,
            "iat": now,
            "scope": scope,
            "sub": str(user_id),
            "user_id": user_id,
        }
        return jwt.encode(payload, cls._secret, algorithm="HS256")  # type: ignore

    @classmethod
    def encode_token(cls, user_id: int) -> str:
        """Create an access JWT for a given user ID."""
        return cls._generate_token(
            user_id=user_id,
            scope="accessToken",
            expires_delta=timedelta(seconds=cls._access_cookie_max_age),
        )

    @classmethod
    def decode_token(cls, token: str) -> int:
        """Decode an access token and return the user ID, or raise if invalid."""
        try:
            payload = jwt.decode(token, cls._secret, algorithms=["HS256"])  # type: ignore
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Token expired") from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e

        if payload.get("scope") != "accessToken":
            raise HTTPException(
                status_code=401,
                detail="Scope for the token is invalid",
            )
        return int(payload["user_id"])

    @classmethod
    def encode_refresh_token(cls, user_id: int) -> str:
        """Create a refresh JWT for a given user ID."""
        return cls._generate_token(
            user_id=user_id,
            scope="refreshToken",
            expires_delta=timedelta(seconds=cls._refresh_cookie_max_age),
        )

    @classmethod
    def decode_refresh_token(cls, token: str) -> int:
        """Decode a refresh token and return the user ID, or raise if invalid."""
        try:
            payload = jwt.decode(token, cls._secret, algorithms=["HS256"])  # type: ignore
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Refresh token expired") from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid refresh token") from e

        if payload.get("scope") != "refreshToken":
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        return int(payload["user_id"])

    @classmethod
    def set_auth_cookies(
        cls, response: ORJSONResponse, access_token: str, refresh_token: str
    ) -> None:
        """Set authentication cookies with access and refresh tokens."""
        cookie_params: dict[str, Any] = {
            "path": "/",
            "secure": not settings.reload,
            "httponly": True,
            "samesite": "lax",
            "domain": settings.jwt_cookie_domain,
        }
        response.set_cookie(
            key="accessToken",
            value=access_token,
            max_age=cls._access_cookie_max_age,
            **cookie_params,
        )
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            max_age=cls._refresh_cookie_max_age,
            **cookie_params,
        )

    @classmethod
    def clear_auth_cookies(cls, response: ORJSONResponse) -> None:
        """Clear authentication cookies from the response."""
        cookie_params: dict[str, Any] = {
            "path": "/",
            "secure": not settings.reload,
            "httponly": True,
            "samesite": "lax",
            "domain": settings.jwt_cookie_domain,
        }
        response.delete_cookie(
            key="accessToken",
            **cookie_params,
        )
        response.delete_cookie(
            key="refreshToken",
            **cookie_params,
        )
