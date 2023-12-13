from marshmallow import fields, post_load
from griptape.schemas import BaseSchema


class PromptStackInputSchema(BaseSchema):
    content = fields.Str()
    role = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.utils.prompt_stack import PromptStack

        return PromptStack.Input(**data)
