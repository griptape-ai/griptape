from attrs import define, field

from griptape.drivers import BasePromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class StructureTaskMemorySummaryEngineConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(metadata={"save": True})
