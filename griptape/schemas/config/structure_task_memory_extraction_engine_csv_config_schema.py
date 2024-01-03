from marshmallow import fields, post_load
from griptape.schemas import BaseSchema, PolymorphicSchema


class StructureTaskMemoryExtractionEngineCsvConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    prompt_driver = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.config import StructureTaskMemoryExtractionEngineCsvConfig

        return StructureTaskMemoryExtractionEngineCsvConfig(**data, **kwargs)
