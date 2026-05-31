from pydantic import EmailStr, Field

from app.web.schemas import CamelCaseModel


class LoginRequest(CamelCaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponse(CamelCaseModel):
    """Response schema containing access and refresh tokens."""

    access_token: str
    refresh_token: str


class RefreshRequest(CamelCaseModel):
    """Request schema for token refresh."""

    refresh_token: str
