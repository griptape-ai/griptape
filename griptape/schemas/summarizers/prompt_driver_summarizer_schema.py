from marshmallow import fields
from griptape.schemas import PolymorphicSchema, SummarizerSchema


class PromptDriverSummarizerSchema(SummarizerSchema):
    driver = fields.Nested(PolymorphicSchema())

    def make_obj(self, data, **kwargs):
        from griptape.summarizers import PromptDriverSummarizer

        return PromptDriverSummarizer(**data)
