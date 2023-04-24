from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema


class SummarizerSchema(BaseSchema):
    class Meta:
        ordered = True

    type = fields.Str(required=True)

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
