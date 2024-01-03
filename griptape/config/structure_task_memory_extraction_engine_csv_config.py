from attrs import define, field

from griptape.drivers import BasePromptDriver


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineCsvConfig:
    prompt_driver: BasePromptDriver = field()
