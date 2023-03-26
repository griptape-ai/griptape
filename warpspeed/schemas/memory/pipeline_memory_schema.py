from marshmallow import fields, post_load
from warpspeed.schemas import BaseSchema, PipelineRunSchema


class PipelineMemorySchema(BaseSchema):
    class Meta:
        ordered = True

    type = fields.Str(required=True)
    runs = fields.List(fields.Nested(PipelineRunSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.memory import PipelineMemory

        return PipelineMemory(**data)
