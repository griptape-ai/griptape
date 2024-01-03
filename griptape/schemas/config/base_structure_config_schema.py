from marshmallow import fields
from abc import abstractmethod
from griptape.schemas import BaseSchema, PolymorphicSchema, StructureTaskMemoryConfigSchema


class BaseStructureConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    prompt_driver = fields.Nested(PolymorphicSchema())
    task_memory = fields.Nested(StructureTaskMemoryConfigSchema())

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
