from marshmallow import fields, post_load
from griptape.schemas import PipelineMemorySchema, PolymorphicSchema


class SummaryPipelineMemorySchema(PipelineMemorySchema):
    offset = fields.Int()
    summary = fields.Str()
    summary_index = fields.Int()
    summarizer = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory import SummaryPipelineMemory

        return SummaryPipelineMemory(**data)
