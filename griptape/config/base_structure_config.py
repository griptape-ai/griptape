from __future__ import annotations

from abc import ABC
from typing import Optional

from attr import define, field

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
    overrides: dict = field(default={}, kw_only=True, metadata={"serializable": True})

    def _factory(self, cls: type, overrides_namespace: str, **params):
        """Factory method to create a new instance of the class with the given parameters

        Args:
            :param cls: the class to instantiate
            :param overrides_namespace: the namespace to look for values in the overrides dictionary
            :param params: the parameters to pass to the class

        Returns:
            :return: a new instance of the class
        """
        return cls(**{**params, **self.overrides.get(overrides_namespace, {})})
