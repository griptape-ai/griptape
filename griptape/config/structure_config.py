from attrs import define, field

from griptape.config import PromptDriverConfig, StructureTaskMemoryConfig


@define(kw_only=True)
class StructureConfig:
    prompt_driver: PromptDriverConfig = field()
    task_memory: StructureTaskMemoryConfig = field()
