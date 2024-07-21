from __future__ import annotations

from typing import Optional

from attrs import Factory, define, field

from griptape.config import BaseStructureConfig
from griptape.drivers import (
    BaseAudioTranscriptionDriver,
    BaseConversationMemoryDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseTextToSpeechDriver,
    BaseVectorStoreDriver,
    DummyAudioTranscriptionDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyImageQueryDriver,
    DummyPromptDriver,
    DummyTextToSpeechDriver,
    DummyVectorStoreDriver,
)


@define
class StructureConfig(BaseStructureConfig):
    prompt_driver: BasePromptDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyPromptDriver()),
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyImageGenerationDriver()),
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyImageQueryDriver()),
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyEmbeddingDriver()),
        metadata={"serializable": True},
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda: DummyVectorStoreDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=Factory(lambda: DummyTextToSpeechDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: DummyAudioTranscriptionDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
