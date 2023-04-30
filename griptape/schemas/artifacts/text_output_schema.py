from marshmallow import post_load
from griptape.schemas import ArtifactSchema


class TextOutputSchema(ArtifactSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import TextOutput

        return TextOutput(**data)
