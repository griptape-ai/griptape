from marshmallow import fields, post_load
from griptape.schemas import ConversationMemorySchema


class BufferConversationMemorySchema(ConversationMemorySchema):
    buffer_size = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.structure import BufferConversationMemory

        return BufferConversationMemory(**data)
