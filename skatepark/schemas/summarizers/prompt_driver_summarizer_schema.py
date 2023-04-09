from marshmallow import fields
from skatepark.schemas import PolymorphicSchema, SummarizerSchema


class PromptDriverSummarizerSchema(SummarizerSchema):
    driver = fields.Nested(PolymorphicSchema())

    def make_obj(self, data, **kwargs):
        from skatepark.summarizers import PromptDriverSummarizer

        return PromptDriverSummarizer(**data)
