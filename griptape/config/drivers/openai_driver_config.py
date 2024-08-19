from attrs import define

from griptape.config.drivers import DriverConfig
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiAudioTranscriptionDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiImageQueryDriver,
    OpenAiTextToSpeechDriver,
)
from griptape.utils.decorators import lazy_property


@define
class OpenAiDriverConfig(DriverConfig):
    @lazy_property()
    def prompt(self) -> OpenAiChatPromptDriver:
        return OpenAiChatPromptDriver(model="gpt-4o")

    @lazy_property()
    def image_generation(self) -> OpenAiImageGenerationDriver:
        return OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512")

    @lazy_property()
    def image_query(self) -> OpenAiImageQueryDriver:
        return OpenAiImageQueryDriver(model="gpt-4o")

    @lazy_property()
    def embedding(self) -> OpenAiEmbeddingDriver:
        return OpenAiEmbeddingDriver(model="text-embedding-3-small")

    @lazy_property()
    def vector_store(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-3-small"))

    @lazy_property()
    def text_to_speech(self) -> OpenAiTextToSpeechDriver:
        return OpenAiTextToSpeechDriver(model="tts")

    @lazy_property()
    def audio_transcription(self) -> OpenAiAudioTranscriptionDriver:
        return OpenAiAudioTranscriptionDriver(model="whisper-1")
