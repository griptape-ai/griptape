from marshmallow import fields, post_load
from griptape.schemas import PromptDriverSchema


class OpenAiPromptDriverSchema(PromptDriverSchema):
    api_type = fields.Str()
    api_version = fields.Str(allow_none=True)
    api_base = fields.Str()
    api_key = fields.Str(allow_none=True)
    organization = fields.Str(allow_none=True)
    model = fields.Str()
    temperature = fields.Float()
    user = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.drivers import OpenAiPromptDriver

        return OpenAiPromptDriver(**data)
