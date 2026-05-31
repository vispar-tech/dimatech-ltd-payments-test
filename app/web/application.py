from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging import configure_logging
from app.settings import settings
from app.web.api.router import api_router
from app.web.handlers import (
    global_exception_handler,
    http_exception_handler,
    pydantic_validation_error_handler,
    response_validation_exception_handler,
    validation_exception_handler,
    value_error_handler,
)
from app.web.lifespan import lifespan_setup
from app.web.responses import ORJSONResponse

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """Create and configure FastAPI application."""
    configure_logging()
    app = FastAPI(
        title="dimatech-ltd-payments-test",
        version="0.1.0",
        lifespan=lifespan_setup,
        default_response_class=ORJSONResponse,
        openapi_url="/api/openapi.json",
        docs_url=None,
        redoc_url=None,
    )

    add_pagination(app)

    app.include_router(api_router, prefix="/api")

    # Register v2-specific exception handlers.
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(
        ResponseValidationError,
        response_validation_exception_handler,
    )
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)

    # Adds static directory.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
    app.state.APP_ROOT = APP_ROOT

    logger.info("Setup middleware CORS for {}", settings.allowed_hosts.split(","))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
