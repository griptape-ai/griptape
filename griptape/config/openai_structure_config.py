from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    BaseAudioTranscriptionDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseTextToSpeechDriver,
    BaseVectorStoreDriver,
    LocalVectorStoreDriver,
    OpenAiAudioTranscriptionDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiImageQueryDriver,
    OpenAiTextToSpeechDriver,
)


@define
class OpenAiStructureConfig(StructureConfig):
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model="gpt-4o")),
        metadata={"serializable": True},
        kw_only=True,
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(lambda: OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512")),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(lambda: OpenAiImageQueryDriver(model="gpt-4o")),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver(model="text-embedding-3-small")),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-3-small")),
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=Factory(lambda: OpenAiTextToSpeechDriver(model="tts")),
        kw_only=True,
        metadata={"serializable": True},
    )
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: OpenAiAudioTranscriptionDriver(model="whisper-1")),
        kw_only=True,
        metadata={"serializable": True},
    )
