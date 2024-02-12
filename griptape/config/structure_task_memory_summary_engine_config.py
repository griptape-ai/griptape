from attrs import Factory, define, field

from griptape.drivers import BasePromptDriver, DummyPromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemorySummaryEngineConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: DummyPromptDriver()), metadata={"serializable": True}
    )
