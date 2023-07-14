from marshmallow import post_load, fields
from griptape.schemas import ArtifactSchema


class CsvRowArtifactSchema(ArtifactSchema):
    value = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(allow_none=True)
    )
    separator = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.artifacts import CsvRowArtifact

        return CsvRowArtifact(**data)
