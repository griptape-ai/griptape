from attrs import define

from griptape.configs.drivers import DriversConfig
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiAudioTranscriptionDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiTextToSpeechDriver,
)
from griptape.utils.decorators import lazy_property


@define
class OpenAiDriversConfig(DriversConfig):
    @lazy_property()
    def prompt_driver(self) -> OpenAiChatPromptDriver:
        return OpenAiChatPromptDriver(model="gpt-4o")

    @lazy_property()
    def image_generation_driver(self) -> OpenAiImageGenerationDriver:
        return OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512")

    @lazy_property()
    def embedding_driver(self) -> OpenAiEmbeddingDriver:
        return OpenAiEmbeddingDriver(model="text-embedding-3-small")

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-3-small"))

    @lazy_property()
    def text_to_speech_driver(self) -> OpenAiTextToSpeechDriver:
        return OpenAiTextToSpeechDriver(model="tts-1")

    @lazy_property()
    def audio_transcription_driver(self) -> OpenAiAudioTranscriptionDriver:
        return OpenAiAudioTranscriptionDriver(model="whisper-1")
