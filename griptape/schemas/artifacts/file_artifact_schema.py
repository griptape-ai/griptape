from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema
from griptape.utils.marshmallow.fields import Bytes


class FileArtifactSchema(ArtifactSchema):
    name = fields.Str()
    path = fields.Str()
    value = Bytes()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import FileArtifact

        return FileArtifact(**data)
