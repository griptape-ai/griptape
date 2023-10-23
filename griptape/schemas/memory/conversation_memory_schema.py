from marshmallow import fields, post_load
from griptape.schemas import BaseSchema, RunSchema


class ConversationMemorySchema(BaseSchema):
    type = fields.Str()
    runs = fields.List(fields.Nested(RunSchema()))
    max_runs = fields.Int(allow_none=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.structure import ConversationMemory

        return ConversationMemory(**data)
