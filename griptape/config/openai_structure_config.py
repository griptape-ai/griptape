from attrs import define, Factory, field

from griptape.config import StructureConfig
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiVisionImageQueryDriver,
)


@define
class OpenAiStructureConfig(StructureConfig):
    prompt_driver: OpenAiChatPromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model="gpt-4o")), metadata={"serializable": True}, kw_only=True
    )
    image_generation_driver: OpenAiImageGenerationDriver = field(
        default=Factory(lambda: OpenAiImageGenerationDriver(model="dall-e-2", image_size="512x512")),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: OpenAiVisionImageQueryDriver = field(
        default=Factory(lambda: OpenAiVisionImageQueryDriver(model="gpt-4-vision-preview")),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: OpenAiEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver(model="text-embedding-3-small")),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: LocalVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(model="text-embedding-3-small"))
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
