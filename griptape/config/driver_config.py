from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.config import BaseDriverConfig
from griptape.drivers import (
    DummyAudioTranscriptionDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyImageQueryDriver,
    DummyPromptDriver,
    DummyTextToSpeechDriver,
    DummyVectorStoreDriver,
)

if TYPE_CHECKING:
    from griptape.drivers import (
        BaseAudioTranscriptionDriver,
        BaseConversationMemoryDriver,
        BaseEmbeddingDriver,
        BaseImageGenerationDriver,
        BaseImageQueryDriver,
        BasePromptDriver,
        BaseTextToSpeechDriver,
        BaseVectorStoreDriver,
    )


@define
class DriverConfig(BaseDriverConfig):
    prompt: BasePromptDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyPromptDriver()),
        metadata={"serializable": True},
    )
    image_generation: BaseImageGenerationDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyImageGenerationDriver()),
        metadata={"serializable": True},
    )
    image_query: BaseImageQueryDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyImageQueryDriver()),
        metadata={"serializable": True},
    )
    embedding: BaseEmbeddingDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyEmbeddingDriver()),
        metadata={"serializable": True},
    )
    vector_store: BaseVectorStoreDriver = field(
        default=Factory(lambda: DummyVectorStoreDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
    conversation_memory: Optional[BaseConversationMemoryDriver] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    text_to_speech: BaseTextToSpeechDriver = field(
        default=Factory(lambda: DummyTextToSpeechDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
    audio_transcription: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: DummyAudioTranscriptionDriver()),
        kw_only=True,
        metadata={"serializable": True},
    )
