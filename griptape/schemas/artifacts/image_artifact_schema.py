from marshmallow import post_load, fields
from griptape.schemas import BaseArtifactSchema


class ImageArtifactSchema(BaseArtifactSchema):
    value = fields.Str()
    mime_type = fields.Str()
    width = fields.Int()
    height = fields.Int()
    model = fields.Str()
    prompt = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import ImageArtifact

        return ImageArtifact(**data)
