from marshmallow import post_load, fields
from griptape.schemas import BaseArtifactSchema


class ImageArtifactSchema(BaseArtifactSchema):
    base64 = fields.Str()
    mime_type = fields.Str()
    width = fields.Int()
    height = fields.Int()
    model = fields.Str()
    prompt = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import ImageArtifact

        if "base64" in data:
            import base64

            image_bytes = base64.b64decode(data["base64"])
            data["value"] = image_bytes
            del data["base64"]

        return ImageArtifact(**data)
