import base64
from typing import Any

from marshmallow import ValidationError, fields


class Bytes(fields.Field):
    def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs) -> str:
        return base64.b64encode(value).decode()

    def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs) -> bytes:
        return base64.b64decode(value)

    def _validate(self, value: Any) -> None:
        if not isinstance(value, bytes):
            raise ValidationError("Invalid input type.")
