from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from griptape.configs.drivers import BaseDriversConfig
from griptape.drivers import (
    DummyAudioTranscriptionDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyPromptDriver,
    DummyTextToSpeechDriver,
    DummyVectorStoreDriver,
    LocalConversationMemoryDriver,
    LocalRulesetDriver,
)
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from griptape.drivers import (
        BaseAudioTranscriptionDriver,
        BaseConversationMemoryDriver,
        BaseEmbeddingDriver,
        BaseImageGenerationDriver,
        BasePromptDriver,
        BaseRulesetDriver,
        BaseTextToSpeechDriver,
        BaseVectorStoreDriver,
    )


@define
class DriversConfig(BaseDriversConfig):
    @lazy_property()
    def prompt_driver(self) -> BasePromptDriver:
        return DummyPromptDriver()

    @lazy_property()
    def image_generation_driver(self) -> BaseImageGenerationDriver:
        return DummyImageGenerationDriver()

    @lazy_property()
    def embedding_driver(self) -> BaseEmbeddingDriver:
        return DummyEmbeddingDriver()

    @lazy_property()
    def vector_store_driver(self) -> BaseVectorStoreDriver:
        return DummyVectorStoreDriver(embedding_driver=self.embedding_driver)

    @lazy_property()
    def conversation_memory_driver(self) -> BaseConversationMemoryDriver:
        return LocalConversationMemoryDriver()

    @lazy_property()
    def text_to_speech_driver(self) -> BaseTextToSpeechDriver:
        return DummyTextToSpeechDriver()

    @lazy_property()
    def audio_transcription_driver(self) -> BaseAudioTranscriptionDriver:
        return DummyAudioTranscriptionDriver()

    @lazy_property()
    def ruleset_driver(self) -> BaseRulesetDriver:
        return LocalRulesetDriver()
