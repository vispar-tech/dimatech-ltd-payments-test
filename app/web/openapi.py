import logging
from typing import Any

from fastapi import FastAPI

from app.web.handlers import (
    HTTPValidationError,
    ValidationError,
)
from app.web.responses import BaseResponse

logger = logging.getLogger(__name__)


# Constants
DEFAULT_SKIP_PATHS = ["/docs", "/redoc", "/swagger-redirect", "/openapi.json"]

HTTP_STATUS_ERROR_4XX = "4"
HTTP_STATUS_ERROR_5XX = "5"
JSON_CONTENT_TYPE = "application/json"
ARRAY_TYPE = "array"
OBJECT_TYPE = "object"


MODEL_NAME_MAPPING: dict[str, str] = {
    # Example: "Body_login_user_credentials": "LoginUserRequest",
}


def _ensure_openapi_schema(app: FastAPI) -> None:
    """Ensure OpenAPI schema is initialized.

    Args:
        app: FastAPI application instance.
    """
    if not app.openapi_schema:
        app.openapi_schema = app.openapi()


def _get_schemas_component(app: FastAPI) -> dict[str, Any]:
    """Get schemas component from OpenAPI schema.

    Args:
        app: FastAPI application instance.

    Returns:
        Schemas dictionary from OpenAPI components.
    """
    if not app.openapi_schema:
        return {}
    return app.openapi_schema.setdefault("components", {}).setdefault("schemas", {})


def _register_base_response_schema(schemas: dict[str, Any]) -> None:
    """Register BaseResponse schema in OpenAPI.

    Args:
        schemas: Schemas dictionary to update.
    """
    if "BaseResponse" in schemas:
        return

    base_response_schema = BaseResponse.model_json_schema(
        ref_template="#/components/schemas/{model}",
        mode="serialization",
        by_alias=True,
    )
    base_response_schema["properties"]["retExtInfo"].pop("additionalProperties", None)
    schemas["BaseResponse"] = base_response_schema


def _register_error_schema(
    schemas: dict[str, Any],
    schema_name: str,
    schema_class: type[Any],
) -> None:
    """Register error schema in OpenAPI.

    Args:
        schemas: Schemas dictionary to update.
        schema_name: Name of the schema in OpenAPI.
        schema_class: Pydantic model class.
    """
    error_schema = schema_class.model_json_schema(
        ref_template="#/components/schemas/{model}",
        mode="serialization",
        by_alias=True,
    )
    schemas[schema_name] = error_schema


def _add_additional_schemas(app: FastAPI) -> None:
    """Add additional schemas to OpenAPI schema.

    Args:
        app: FastAPI application instance.
    """
    _ensure_openapi_schema(app)
    schemas = _get_schemas_component(app)

    _register_base_response_schema(schemas)
    _register_error_schema(schemas, "ValidationError", ValidationError)
    _register_error_schema(schemas, "HTTPValidationError", HTTPValidationError)


def _replace_schema_refs(schema: Any, old_ref: str, new_ref: str) -> None:
    """Replace schema $ref references recursively.

    Args:
        schema: Schema dictionary/list/any to update.
        old_ref: Old reference path to replace.
        new_ref: New reference path.
    """
    if isinstance(schema, dict):
        if "$ref" in schema and schema["$ref"] == old_ref:
            schema["$ref"] = new_ref
        for value in schema.values():  # type: ignore[arg-type]
            _replace_schema_refs(value, old_ref, new_ref)
    elif isinstance(schema, list):
        for item in schema:  # type: ignore[arg-type]
            _replace_schema_refs(item, old_ref, new_ref)


def _rename_schemas_by_mapping(app: FastAPI) -> None:
    """Rename schemas in OpenAPI based on MODEL_NAME_MAPPING.

    Args:
        app: FastAPI application instance.
    """
    if not app.openapi_schema or not MODEL_NAME_MAPPING:
        return

    schemas = app.openapi_schema.get("components", {}).get("schemas", {})

    for old_name, new_name in MODEL_NAME_MAPPING.items():
        if old_name not in schemas:
            continue

        if new_name in schemas:
            logger.warning(
                "Schema %s already exists, skipping rename from %s",
                new_name,
                old_name,
            )
            continue

        # Rename schema
        schemas[new_name] = schemas.pop(old_name)

        # Update all $ref references
        old_ref_path = f"#/components/schemas/{old_name}"
        new_ref_path = f"#/components/schemas/{new_name}"
        _replace_schema_refs(app.openapi_schema, old_ref_path, new_ref_path)


def _should_skip_path(path: str, skip_paths: list[str]) -> bool:
    """Check if path should be skipped.

    Args:
        path: Path to check.
        skip_paths: List of paths to skip.

    Returns:
        True if path should be skipped.
    """
    return any(skip in path for skip in skip_paths)


def _normalize_array_schema(original_schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize array schema to object schema.

    Args:
        original_schema: Original schema dictionary.

    Returns:
        Normalized schema dictionary.
    """
    if original_schema.get("type") != ARRAY_TYPE:
        return original_schema

    return {
        "type": OBJECT_TYPE,
        "properties": {"items": original_schema},
        "required": ["items"],
    }


def _is_error_status_code(status_code: str) -> bool:
    """Check if status code represents an error.

    Args:
        status_code: HTTP status code as string.

    Returns:
        True if status code is 4xx or 5xx.
    """
    status_str = str(status_code)
    return status_str.startswith((HTTP_STATUS_ERROR_4XX, HTTP_STATUS_ERROR_5XX))


def _wrap_schema_in_base_response(
    schema: dict[str, Any],
    is_error: bool,
) -> dict[str, list[Any]]:
    """Wrap schema in BaseResponse wrapper.

    Args:
        schema: Schema to wrap.
        is_error: Whether this is an error response.

    Returns:
        Wrapped schema with BaseResponse.
    """
    property_key = "retExtInfo" if is_error else "result"

    return {
        "allOf": [
            {"$ref": "#/components/schemas/BaseResponse"},
            {
                "type": OBJECT_TYPE,
                "required": [property_key],
                "properties": {property_key: schema},
            },
        ],
    }


def _wrap_response_schema(response_detail: dict[str, Any]) -> None:
    """Wrap response schema in BaseResponse.

    Args:
        response_detail: Response detail dictionary.
    """
    content = response_detail.get("content", {}).get(JSON_CONTENT_TYPE, {})
    if "schema" not in content:
        return

    original_schema = content["schema"]
    normalized_schema = _normalize_array_schema(original_schema)
    status_code = response_detail.get("status_code", "")
    is_error = _is_error_status_code(status_code)

    wrapped_schema = _wrap_schema_in_base_response(normalized_schema, is_error)
    content["schema"] = wrapped_schema


def _wrap_all_responses(path_item: dict[str, Any]) -> None:
    """Wrap all response schemas in BaseResponse for a path item.

    Args:
        path_item: Path item dictionary.
    """
    for operation in path_item.values():
        responses = operation.get("responses", {})
        for status_code, response_detail in responses.items():
            response_detail["status_code"] = status_code
            _wrap_response_schema(response_detail)


def update_openapi_schema(app: FastAPI, skip_paths: list[str] | None = None) -> None:
    """Update app.openapi_schema with custom wrappers.

    Args:
        app: FastAPI application instance.
        skip_paths: Optional list of paths to skip when wrapping responses.
    """
    skip_paths = skip_paths or DEFAULT_SKIP_PATHS

    _ensure_openapi_schema(app)
    _add_additional_schemas(app)
    _rename_schemas_by_mapping(app)

    if not app.openapi_schema:
        return

    paths = app.openapi_schema.get("paths", {})
    for path, path_item in paths.items():
        if _should_skip_path(path, skip_paths):
            continue

        _wrap_all_responses(path_item)
