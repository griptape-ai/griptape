from marshmallow import fields, post_load
from griptape.schemas import (
    BaseSchema,
    StructureTaskMemoryExtractionEngineJsonConfigSchema,
    StructureTaskMemoryExtractionEngineCsvConfigSchema,
)


class StructureTaskMemoryExtractionEngineConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    csv = fields.Nested(StructureTaskMemoryExtractionEngineCsvConfigSchema)
    json = fields.Nested(StructureTaskMemoryExtractionEngineJsonConfigSchema)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.config import StructureTaskMemoryExtractionEngineConfig

        return StructureTaskMemoryExtractionEngineConfig(**data, **kwargs)
