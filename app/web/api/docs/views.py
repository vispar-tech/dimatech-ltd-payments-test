from fastapi import APIRouter, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def swagger_ui_html(request: Request) -> HTMLResponse:
    """Swagger UI.

    Args:
        request: current request.

    Returns:
        rendered swagger UI.
    """
    title = request.app.title
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{title} - Swagger UI",
        oauth2_redirect_url=str(request.url_for("swagger_ui_redirect")),
        swagger_js_url="/static/docs/swagger-ui-bundle.js",
        swagger_css_url="/static/docs/swagger-ui.css",
        swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
    )


@router.get("/swagger-redirect", include_in_schema=False)
async def swagger_ui_redirect() -> HTMLResponse:
    """
    Redirect to swagger.

    Returns:
        redirect.
    """
    return get_swagger_ui_oauth2_redirect_html()
