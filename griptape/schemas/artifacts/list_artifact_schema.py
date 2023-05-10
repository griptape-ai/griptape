from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema, PolymorphicSchema


class ListArtifactSchema(ArtifactSchema):
    value = fields.List(fields.Nested(PolymorphicSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import ListArtifact

        return ListArtifact(**data)
