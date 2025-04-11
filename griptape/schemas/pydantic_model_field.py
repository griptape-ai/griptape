from __future__ import annotations

from typing import Any, Optional

from marshmallow import fields
from pydantic import BaseModel, RootModel


class PydanticModel(fields.Field):
    def _serialize(self, value: Optional[BaseModel], attr: Any, obj: Any, **kwargs) -> Optional[dict]:
        if value is None:
            return None
        return value.model_dump()

    def _deserialize(self, value: dict, attr: Any, data: Any, **kwargs) -> BaseModel:
        return RootModel(value)
