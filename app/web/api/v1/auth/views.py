from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth.dependencies import get_current_user, get_refresh_token_cookie
from app.services.auth.service import AuthService, get_auth_service
from app.web.api.v1.auth.schemas import LoginRequest, LoginResponse, RefreshRequest
from app.web.responses import ORJSONResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user and set auth cookies",
    operation_id="login_user",
)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ORJSONResponse:
    """Endpoint for user login."""
    return await auth_service.login(email=data.email, password=data.password)


@router.post(
    "/logout",
    summary="Logout user and clear auth cookies",
    operation_id="logout_user",
    dependencies=[Depends(get_current_user)],
)
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> ORJSONResponse:
    """Endpoint for user logout."""
    return auth_service.logout()


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access and refresh tokens",
    operation_id="refresh_token",
)
async def refresh_token(
    refresh_req: RefreshRequest | None = None,
    refresh_token: str | None = Depends(get_refresh_token_cookie),
    auth_service: AuthService = Depends(get_auth_service),
) -> ORJSONResponse:
    """Endpoint to refresh access and refresh tokens.

    Accepts token from a request body or from cookie.
    """
    token = None
    token = refresh_req.refresh_token if refresh_req is not None else refresh_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return await auth_service.refresh(refresh_token=token)
