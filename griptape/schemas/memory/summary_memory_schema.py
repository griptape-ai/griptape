from marshmallow import fields, post_load
from griptape.schemas import MemorySchema, PolymorphicSchema


class SummaryPipelineMemorySchema(MemorySchema):
    offset = fields.Int()
    summary = fields.Str()
    summary_index = fields.Int()
    summarizer = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory import SummaryMemory

        return SummaryMemory(**data)
