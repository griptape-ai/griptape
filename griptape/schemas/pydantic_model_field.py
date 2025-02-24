from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from marshmallow import fields

if TYPE_CHECKING:
    from pydantic import BaseModel


class PydanticModel(fields.Field):
    def _serialize(self, value: Optional[BaseModel], attr: Any, obj: Any, **kwargs) -> Optional[dict]:
        if value is None:
            return None
        return value.model_dump()

    def _deserialize(self, value: dict, attr: Any, data: Any, **kwargs) -> dict:
        # Not implemented as it is non-trivial to deserialize json back into a model
        # since we need to know the model class to instantiate it.
        # Would rather not implement right now rather than implement incorrectly.
        raise NotImplementedError("Model fields cannot be deserialized directly.")
