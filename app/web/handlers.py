import logging
from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from app.web.responses import BaseResponse, ORJSONResponse

logger = logging.getLogger(__name__)


class ValidationError(BaseModel):
    """Represent a validation error item."""

    field: str
    message: str
    type: str


class HTTPValidationError(BaseModel):
    """Contain a list of validation errors for HTTP validation."""

    errors: list[ValidationError]


def parse_validation_errors(
    validation_error: RequestValidationError
    | ResponseValidationError
    | PydanticValidationError,
) -> list[ValidationError]:
    """Parse validation errors into a standardized format."""
    errors: list[ValidationError] = []
    for error in validation_error.errors():
        msg_raw = error.get("msg") or error.get("message") or error.get("msg", "")
        message = str(msg_raw) if not isinstance(msg_raw, str) else msg_raw
        errors.append(
            ValidationError(
                field=".".join(str(loc) for loc in error.get("loc", [])),
                message=message,
                type=error.get("type", "validation_error"),
            )
        )
    return errors


def build_response(
    *,
    status_code: int,
    msg: str,
    ret_ext_info: dict[str, Any] | None = None,
    result: Any = None,
) -> ORJSONResponse:
    """Build a standard API response using ORJSONResponse."""
    ret_ext_info = ret_ext_info or {}
    response_dict = BaseResponse(
        code=status_code,
        msg=msg,
        ret_ext_info=ret_ext_info,
    ).model_dump(by_alias=False)
    response_dict["result"] = result if result is not None else {}
    return ORJSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response_dict),
    )


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle HTTP exceptions and return a formatted response."""
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    detail = exc.detail
    ret_ext_info: dict[str, Any]
    if isinstance(detail, dict | BaseModel):
        ret_ext_info = (
            detail.model_dump(by_alias=True)
            if isinstance(detail, BaseModel)
            else detail
        )
        msg = "An error occurred while processing the request"
    else:
        ret_ext_info = {}
        msg = detail
    return build_response(
        status_code=exc.status_code,
        msg=msg,
        ret_ext_info=ret_ext_info,
    )


async def validation_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle request validation errors and return a formatted response."""
    if not isinstance(exc, RequestValidationError):
        raise exc
    errors = parse_validation_errors(exc)
    return build_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        msg="Validation error",
        ret_ext_info=HTTPValidationError(errors=errors).model_dump(),
    )


async def response_validation_exception_handler(
    request: Request,
    exc: Exception,
) -> Response:
    """Handle response validation errors and return a server error response."""
    if not isinstance(exc, ResponseValidationError):
        raise exc
    errors = parse_validation_errors(exc)
    logger.error(f"Response Validation Error: {exc}")
    return build_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        msg="Response validation error",
        ret_ext_info=HTTPValidationError(errors=errors).model_dump(),
    )


async def pydantic_validation_error_handler(
    request: Request,
    exc: Exception,
) -> Response:
    """Handle Pydantic validation errors and return a formatted response."""
    if not isinstance(exc, PydanticValidationError):
        raise exc
    errors = parse_validation_errors(exc)
    return build_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        msg="Validation error",
        ret_ext_info=HTTPValidationError(errors=errors).model_dump(),
    )


async def value_error_handler(request: Request, exc: Exception) -> Response:
    """Handle generic ValueErrors and return a bad request response."""
    if isinstance(exc, PydanticValidationError):
        return await pydantic_validation_error_handler(request, exc)
    logger.error(f"Value Error: {exc}")
    return build_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        msg=str(exc),
    )


async def global_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle all uncaught exceptions and return an internal server error response."""
    if isinstance(exc, PydanticValidationError):
        return await pydantic_validation_error_handler(request, exc)
    logger.exception(f"Exception handled by global handler: {exc!s}")
    return build_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        msg="An error occurred while processing the request",
    )
