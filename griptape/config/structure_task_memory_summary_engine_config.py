from attrs import define, field

from griptape.config import PromptDriverConfig


@define(kw_only=True)
class StructureTaskMemorySummaryEngineConfig:
    prompt_driver: PromptDriverConfig = field()
