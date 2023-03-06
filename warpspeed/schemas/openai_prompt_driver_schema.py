from marshmallow import Schema, fields, post_load
from warpspeed.schemas import PolymorphicSchema


class OpenAiPromptDriverSchema(Schema):
    tokenizer = fields.Nested(PolymorphicSchema())
    temperature = fields.Float()
    user = fields.Str()

    @post_load
    def make_driver(self, data, **kwargs):
        from warpspeed.drivers import OpenAiPromptDriver

        return OpenAiPromptDriver(**data)
