from marshmallow import fields, post_load
from griptape.schemas import MemorySchema


class SummaryMemorySchema(MemorySchema):
    offset = fields.Int()
    summary = fields.Str(allow_none=True)
    summary_index = fields.Int()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory import SummaryMemory

        return SummaryMemory(**data)
