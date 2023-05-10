from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema


class ArtifactSchema(BaseSchema):
    class Meta:
        ordered = True

    type = fields.Str()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
