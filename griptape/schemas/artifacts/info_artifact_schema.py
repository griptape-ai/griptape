from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema


class InfoArtifactSchema(ArtifactSchema):
    value = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import InfoArtifact

        return InfoArtifact(**data)
