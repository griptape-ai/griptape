from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema


class TextArtifactSchema(ArtifactSchema):
    value = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import TextArtifact

        return TextArtifact(**data)
