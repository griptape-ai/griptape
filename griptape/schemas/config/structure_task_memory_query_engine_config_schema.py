from marshmallow import fields, post_load
from griptape.schemas import BaseSchema, PolymorphicSchema


class StructureTaskMemoryQueryEngineConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    prompt_driver = fields.Nested(PolymorphicSchema())
    vector_store_driver = fields.Nested(PolymorphicSchema())

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.config import StructureTaskMemoryQueryEngineConfig

        return StructureTaskMemoryQueryEngineConfig(**data, **kwargs)
