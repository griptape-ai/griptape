from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseEventSchema


class BasePromptEventSchema(BaseEventSchema):
    token_count = fields.Int()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
