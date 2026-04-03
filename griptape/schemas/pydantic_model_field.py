from __future__ import annotations

from typing import Any

from marshmallow import fields
from pydantic import BaseModel, RootModel


class PydanticModel(fields.Field):
    def _serialize(self, value: BaseModel | None, attr: Any, obj: Any, **kwargs) -> dict | None:
        if value is None:
            return None
        return value.model_dump()

    def _deserialize(self, value: dict, attr: Any, data: Any, **kwargs) -> BaseModel:
        return RootModel(value)
