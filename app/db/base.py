import logging
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

meta = MetaData()


class Base(DeclarativeBase):
    """Base for all models."""

    __abstract__ = True
    metadata = meta

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert model to dict with property fields, optionally excluding keys."""
        exclude = exclude or set()
        property_fields = [
            prop.__name__
            for prop in inspect(self.__class__).all_orm_descriptors
            if isinstance(prop, hybrid_property)
        ]
        try:
            result = {**self.__dict__}
            for prop in property_fields:
                if prop in exclude:
                    continue
                try:
                    result[prop] = getattr(self, prop)
                except AttributeError as err:
                    logger.error(f"Error on {prop}: {err}")
                    result[prop] = None
            for key in list(result.keys()):
                if key in exclude:
                    result.pop(key)
            return result
        except AttributeError as err:
            logger.error(f"Error on {self.__class__.__name__}: {err}")
            raise

    def __repr__(self) -> str:
        """
        Return a pretty representation of the model.

        Returns:
            The representation.
        """
        self_dict = self.to_dict()
        items = list(self_dict.items())[:2]
        params = ", ".join([f"{key}={value!r}" for key, value in items])
        if len(items) < len(self_dict):
            params += ", ..."
        return f"{self.__class__.__name__}({params})"
