from attrs import define, field, Factory

from griptape.drivers import BasePromptDriver, DummyPromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryExtractionEngineCsvConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: DummyPromptDriver()), metadata={"serializable": True}
    )
