from marshmallow import fields
from warpspeed.schemas import PolymorphicSchema, SummarizerSchema


class PromptDriverSummarizerSchema(SummarizerSchema):
    driver = fields.Nested(PolymorphicSchema())

    def make_obj(self, data, **kwargs):
        from warpspeed.summarizers import PromptDriverSummarizer

        return PromptDriverSummarizer(**data)
