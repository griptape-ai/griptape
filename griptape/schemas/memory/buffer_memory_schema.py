from marshmallow import fields, post_load
from griptape.schemas import MemorySchema


class BufferPipelineMemorySchema(MemorySchema):
    buffer_size = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory import BufferMemory

        return BufferMemory(**data)
