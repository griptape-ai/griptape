from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define

from griptape.config.drivers import BaseDriverConfig
from griptape.drivers import (
    DummyAudioTranscriptionDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyImageQueryDriver,
    DummyPromptDriver,
    DummyTextToSpeechDriver,
    DummyVectorStoreDriver,
)
from griptape.utils.decorators import lazy_property

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
    @lazy_property()
    def prompt(self) -> BasePromptDriver:
        return DummyPromptDriver()

    @lazy_property()
    def image_generation(self) -> BaseImageGenerationDriver:
        return DummyImageGenerationDriver()

    @lazy_property()
    def image_query(self) -> BaseImageQueryDriver:
        return DummyImageQueryDriver()

    @lazy_property()
    def embedding(self) -> BaseEmbeddingDriver:
        return DummyEmbeddingDriver()

    @lazy_property()
    def vector_store(self) -> BaseVectorStoreDriver:
        return DummyVectorStoreDriver(embedding_driver=self.embedding)

    @lazy_property()
    def conversation_memory(self) -> Optional[BaseConversationMemoryDriver]:
        return None

    @lazy_property()
    def text_to_speech(self) -> BaseTextToSpeechDriver:
        return DummyTextToSpeechDriver()

    @lazy_property()
    def audio_transcription(self) -> BaseAudioTranscriptionDriver:
        return DummyAudioTranscriptionDriver()
