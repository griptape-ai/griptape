from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from attrs import define, field

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
class BaseDriverConfig(ABC):
    prompt: BasePromptDriver = field(kw_only=True, metadata={"serializable": True})
    image_generation: BaseImageGenerationDriver = field(kw_only=True, metadata={"serializable": True})
    image_query: BaseImageQueryDriver = field(kw_only=True, metadata={"serializable": True})
    embedding: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})
    vector_store: BaseVectorStoreDriver = field(kw_only=True, metadata={"serializable": True})
    conversation_memory: Optional[BaseConversationMemoryDriver] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    text_to_speech: BaseTextToSpeechDriver = field(kw_only=True, metadata={"serializable": True})
    audio_transcription: BaseAudioTranscriptionDriver = field(kw_only=True, metadata={"serializable": True})
