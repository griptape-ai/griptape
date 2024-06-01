from __future__ import annotations

from abc import ABC
from typing import Optional, Any

from attrs import define, field

from griptape.config import BaseConfig
from griptape.drivers import (
    BaseConversationMemoryDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    BaseTextToSpeechDriver,
)


@define
class BaseStructureConfig(BaseConfig, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"serializable": True})
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True, metadata={"serializable": True})
    image_query_driver: BaseImageQueryDriver = field(kw_only=True, metadata={"serializable": True})
    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True, metadata={"serializable": True})
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    text_to_speech_driver: BaseTextToSpeechDriver = field(kw_only=True, metadata={"serializable": True})

    def merge_config(self, config: dict) -> BaseStructureConfig:
        for key, value in config.items():
            self._merge_config_rec(key, value)

        return self

    def _merge_config_rec(self, key: str, value: Any) -> BaseStructureConfig:
        if hasattr(self, key):
            if isinstance(value, dict):
                for k, v in value.items():
                    self._merge_config_rec(k, v)
            else:
                setattr(self, key, value)

        return self
