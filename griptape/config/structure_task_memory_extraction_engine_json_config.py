from attrs import define, field, Factory

from griptape.drivers import BasePromptDriver, NopPromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryExtractionEngineJsonConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: NopPromptDriver()), metadata={"serializable": True}
    )
