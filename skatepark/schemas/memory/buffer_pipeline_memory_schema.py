from marshmallow import fields, post_load
from skatepark.schemas import BaseSchema, PipelineRunSchema, PipelineMemorySchema


class BufferPipelineMemorySchema(PipelineMemorySchema):
    buffer_size = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.memory import BufferPipelineMemory

        return BufferPipelineMemory(**data)
