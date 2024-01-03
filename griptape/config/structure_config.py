from attrs import define, field

from .structure_task_memory_config import StructureTaskMemoryConfig
from griptape.drivers import BasePromptDriver


@define(kw_only=True)
class StructureConfig:
    prompt_driver: BasePromptDriver = field()
    task_memory: StructureTaskMemoryConfig = field()
