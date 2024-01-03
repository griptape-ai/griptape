from attrs import define, field

from griptape.drivers import BasePromptDriver


@define(kw_only=True)
class StructureTaskMemorySummaryEngineConfig:
    prompt_driver: BasePromptDriver = field()
