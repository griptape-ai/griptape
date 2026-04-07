from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from griptape.configs.drivers import BaseDriversConfig
from griptape.drivers.audio_transcription.dummy import DummyAudioTranscriptionDriver
from griptape.drivers.embedding.dummy import DummyEmbeddingDriver
from griptape.drivers.image_generation.dummy import DummyImageGenerationDriver
from griptape.drivers.memory.conversation.local import LocalConversationMemoryDriver
from griptape.drivers.prompt.dummy import DummyPromptDriver
from griptape.drivers.ruleset.local import LocalRulesetDriver
from griptape.drivers.text_to_speech.dummy import DummyTextToSpeechDriver
from griptape.drivers.vector.dummy import DummyVectorStoreDriver
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from griptape.drivers.audio_transcription import BaseAudioTranscriptionDriver
    from griptape.drivers.embedding import BaseEmbeddingDriver
    from griptape.drivers.image_generation import BaseImageGenerationDriver
    from griptape.drivers.memory.conversation import BaseConversationMemoryDriver
    from griptape.drivers.prompt import BasePromptDriver
    from griptape.drivers.ruleset import BaseRulesetDriver
    from griptape.drivers.text_to_speech import BaseTextToSpeechDriver
    from griptape.drivers.vector import BaseVectorStoreDriver


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
