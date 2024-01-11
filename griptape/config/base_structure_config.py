from __future__ import annotations
from abc import ABC
from attr import define, field
from griptape.config import StructureTaskMemoryConfig
from griptape.drivers import BasePromptDriver
from griptape.mixins import SerializableMixin
from griptape.schemas.base_schema import BaseSchema
from marshmallow import class_registry, Schema


@define
class BaseStructureConfig(SerializableMixin, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"serialize": True})
    task_memory: StructureTaskMemoryConfig = field(kw_only=True, metadata={"serialize": True})

    @classmethod
    def try_get_schema(cls: type[BaseStructureConfig], obj_type: str) -> list[type[Schema]] | type[Schema]:
        from griptape.config import OpenAiStructureConfig

        class_registry.register("OpenAiStructureConfig", BaseSchema.from_attrscls(OpenAiStructureConfig))

        return class_registry.get_class(obj_type)
