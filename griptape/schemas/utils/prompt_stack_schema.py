from marshmallow import fields, post_load
from griptape.schemas import BaseSchema
from .prompt_stack_input_schema import PromptStackInputSchema


class PromptStackSchema(BaseSchema):
    inputs = fields.List(fields.Nested(PromptStackInputSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.utils.prompt_stack import PromptStack

        return PromptStack(**data)
