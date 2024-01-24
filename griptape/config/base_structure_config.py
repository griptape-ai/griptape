from __future__ import annotations
from typing import Optional
from abc import ABC
from attr import define, field
from griptape.utils import dict_merge
from griptape.config import BaseConfig
from griptape.config import StructureTaskMemoryConfig
from griptape.drivers import BasePromptDriver, BaseImageGenerationDriver, BaseConversationMemoryDriver


@define
class BaseStructureConfig(BaseConfig, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"serializable": True})
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True, metadata={"serializable": True})
    task_memory: StructureTaskMemoryConfig = field(kw_only=True, metadata={"serializable": True})
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        kw_only=True, default=None, metadata={"serializable": True}
    )

    def merge_config(self, config: dict) -> BaseStructureConfig:
        base_config = self.to_dict()
        merged_config = dict_merge(base_config, config)

        return BaseStructureConfig.from_dict(merged_config)
