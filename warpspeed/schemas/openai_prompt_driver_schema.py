from marshmallow import fields, post_load
from warpspeed.schemas import PromptDriverSchema


class OpenAiPromptDriverSchema(PromptDriverSchema):
    temperature = fields.Float()
    user = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from warpspeed.drivers import OpenAiPromptDriver

        return OpenAiPromptDriver(**data)
