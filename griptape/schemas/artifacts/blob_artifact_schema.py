from marshmallow import post_load, fields
from griptape.schemas import BaseArtifactSchema, Bytes


class BlobArtifactSchema(BaseArtifactSchema):
    name = fields.Str()
    dir_name = fields.Str(allow_none=True)
    value = Bytes()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import BlobArtifact

        return BlobArtifact(**data)
