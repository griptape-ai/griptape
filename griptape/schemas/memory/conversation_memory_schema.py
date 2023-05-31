from marshmallow import fields, post_load
from griptape.schemas import BaseSchema, RunSchema


class ConversationMemorySchema(BaseSchema):
    class Meta:
        ordered = True

    type = fields.Str()
    runs = fields.List(fields.Nested(RunSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.structure import ConversationMemory

        return ConversationMemory(**data)
