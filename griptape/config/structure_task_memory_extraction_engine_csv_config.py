from attrs import define, field, Factory

from griptape.drivers import BasePromptDriver, NopPromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineCsvConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(default=Factory(lambda: NopPromptDriver()), metadata={"serializable": True})
