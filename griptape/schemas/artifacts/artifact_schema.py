from abc import abstractmethod
from marshmallow import fields
from griptape.schemas import BaseSchema


class BaseArtifactSchema(BaseSchema):
    id = fields.Str()
    name = fields.Str()
    meta = fields.Dict(keys=fields.Str())
    type = fields.Str()

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
