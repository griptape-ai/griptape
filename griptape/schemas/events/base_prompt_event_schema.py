from abc import abstractmethod
from marshmallow import fields
from griptape.schemas.utils.prompt_stack_schema import PromptStackSchema
from griptape.schemas import BaseEventSchema


class BasePromptEventSchema(BaseEventSchema):
    token_count = fields.Int()
    prompt_stack = fields.Nested(PromptStackSchema())
    prompt = fields.Str()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
