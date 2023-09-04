import base64
from marshmallow import fields, ValidationError


class Bytes(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return base64.b64encode(value).decode()

    def _deserialize(self, value, attr, data, **kwargs):
        return base64.b64decode(value)

    def _validate(self, value):
        if not isinstance(value, bytes):
            raise ValidationError("Invalid input type.")
