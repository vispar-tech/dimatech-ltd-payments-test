from typing import Any

import orjson
from fastapi.responses import Response
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""

    code: int
    msg: str
    ret_ext_info: dict[str, Any] = Field(
        serialization_alias="retExtInfo",
    )


class ORJSONResponse(Response):
    """Custom ORJSON response."""

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        """Render response using orjson."""
        if isinstance(content, dict) and "result" in content:
            result = dict(content.get("result", {}))  # type: ignore
            base_response = BaseResponse(
                code=int(content.get("code", 0)),  # type: ignore
                msg=str(content.get("msg", "OK")),  # type: ignore
                ret_ext_info=dict(content.get("ret_ext_info", {})),  # type: ignore
            )
        elif isinstance(content, list):
            result = {"items": content}  # type: ignore
            base_response = BaseResponse(
                code=0,
                msg="OK",
                ret_ext_info={},
            )
        else:
            result = content or {}  # type: ignore
            base_response = BaseResponse(
                code=0,
                msg="OK",
                ret_ext_info={},
            )

        response_dict = base_response.model_dump(by_alias=True)
        response_dict["result"] = result

        return orjson.dumps(response_dict)
