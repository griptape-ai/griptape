from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema
from griptape.utils.marshmallow.fields import Bytes


class BlobArtifactSchema(ArtifactSchema):
    name = fields.Str()
    dir = fields.Str(allow_none=True)
    value = Bytes()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import BlobArtifact

        return BlobArtifact(**data)
