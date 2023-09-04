from marshmallow import post_load, fields
from griptape.schemas import BaseArtifactSchema, PolymorphicSchema


class ListArtifactSchema(BaseArtifactSchema):
    value = fields.List(fields.Nested(PolymorphicSchema()))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import ListArtifact

        return ListArtifact(**data)
