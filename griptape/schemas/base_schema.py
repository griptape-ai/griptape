from marshmallow import Schema, fields, post_dump


class BaseSchema(Schema):
    schema_namespace = fields.Str(allow_none=True)

    @post_dump
    def remove_null_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }
