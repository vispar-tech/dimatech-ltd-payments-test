from typing import (
    TypeVar,
)

from fastapi import Query
from fastapi_pagination import Page as BasePage
from fastapi_pagination.customization import (
    CustomizedPage,
    UseFieldsAliases,
    UseName,
    UseParamsFields,
)
from pydantic import (
    BaseModel,
    ConfigDict,
)
from pydantic.alias_generators import to_camel

T = TypeVar("T")

Paginated = CustomizedPage[
    BasePage[T],
    UseName("Paginated"),
    UseParamsFields(
        size=Query(10, ge=1, le=100, alias="pageSize"),
        page=Query(1, ge=1, alias="pageNumber"),
    ),
    UseFieldsAliases(
        size="pageSize",
        page="pageNumber",
        pages="totalPages",
        total="totalItems",
    ),
]


class CamelCaseModel(BaseModel):
    """
    A Pydantic model with camelCase aliasing.

    This model only handles camelCase aliasing; no special datetime handling.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
