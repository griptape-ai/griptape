from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema


class ArtifactSchema(BaseSchema):
    class Meta:
        ordered = True

    value = fields.Str()
    type = fields.Str(required=True)

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
