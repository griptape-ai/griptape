from marshmallow import post_load, fields
from griptape.schemas.utils.prompt_stack_schema import PromptStackSchema
from griptape.schemas import BasePromptEventSchema


class StartPromptEventSchema(BasePromptEventSchema):
    prompt_stack = fields.Nested(PromptStackSchema())
    prompt = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartPromptEvent

        return StartPromptEvent(**data)
