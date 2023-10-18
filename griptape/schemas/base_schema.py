from marshmallow import Schema, fields


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)
