from marshmallow import post_load
from griptape.schemas import ArtifactSchema


class ErrorArtifactSchema(ArtifactSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import ErrorArtifact

        return ErrorArtifact(**data)
