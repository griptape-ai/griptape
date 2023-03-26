from marshmallow import fields, post_load
from warpspeed.schemas import BaseSchema, PipelineRunSchema, PipelineMemorySchema


class SummaryPipelineMemorySchema(PipelineMemorySchema):
    offset = fields.Int()
    summary = fields.Str()
    summary_index = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.memory import SummaryPipelineMemory

        return SummaryPipelineMemory(**data)
