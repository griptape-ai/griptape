from marshmallow import fields, post_load
from griptape.schemas import BaseSchema, RunSchema


class MemorySchema(BaseSchema):
    class Meta:
        ordered = True

    type = fields.Str(required=True)
    runs = fields.List(fields.Nested(RunSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory import Memory

        return Memory(**data)
