from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema


class BaseEventSchema(BaseSchema):
    timestamp = fields.Float()
    type = fields.Str()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
