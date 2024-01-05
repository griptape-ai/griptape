from __future__ import annotations
from abc import ABC
from attr import define, field
from griptape.config import StructureTaskMemoryConfig
from griptape.drivers import BasePromptDriver
from griptape.mixins import SerializableMixin
from griptape.schemas.base_schema import BaseSchema
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError


@define
class BaseStructureConfig(SerializableMixin, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"save": True})
    task_memory: StructureTaskMemoryConfig = field(kw_only=True)

    @classmethod
    def from_dict(cls: type[BaseStructureConfig], data: dict) -> BaseStructureConfig:
        from griptape.config import OpenAiStructureConfig

        class_registry.register("OpenAiStructureConfig", BaseSchema.from_attrscls(OpenAiStructureConfig))

        try:
            return class_registry.get_class(data["type"])().load(data)  # pyright: ignore
        except RegistryError:
            raise ValueError("Unsupported type.")
