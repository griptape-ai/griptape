from marshmallow import post_load
from griptape.schemas import BaseStructureConfigSchema


class OpenAiStructureConfigSchema(BaseStructureConfigSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.config import OpenAiStructureConfig

        return OpenAiStructureConfig(**data, **kwargs)
