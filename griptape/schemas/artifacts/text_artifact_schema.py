from marshmallow import post_load, fields
from griptape.schemas import BaseArtifactSchema


class TextArtifactSchema(BaseArtifactSchema):
    value = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import TextArtifact

        return TextArtifact(**data)
