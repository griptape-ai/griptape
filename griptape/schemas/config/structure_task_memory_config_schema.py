from marshmallow import fields, post_load
from griptape.schemas import (
    BaseSchema,
    StructureTaskMemoryQueryEngineConfigSchema,
    StructureTaskMemoryExtractionEngineConfigSchema,
    StructureTaskMemorySummaryEngineConfigSchema,
)


class StructureTaskMemoryConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    query_engine = fields.Nested(StructureTaskMemoryQueryEngineConfigSchema())
    extraction_engine = fields.Nested(StructureTaskMemoryExtractionEngineConfigSchema())
    summary_engine = fields.Nested(StructureTaskMemorySummaryEngineConfigSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.config import StructureTaskMemoryConfig

        return StructureTaskMemoryConfig(**data, **kwargs)
