import os
from typing import Optional
from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
    OpenAiImageGenerationDriver,
    OpenAiImageQueryDriver,
)


@define
class OpenAiStructureConfig(StructureConfig):
    api_key: Optional[str] = field(kw_only=True, default=Factory(lambda: os.getenv("OPENAI_API_KEY")))
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: OpenAiChatPromptDriver(
                model="gpt-4o", api_key=self.api_key, base_url=self.base_url, organization=self.organization
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: OpenAiImageGenerationDriver(
                model="dall-e-2",
                image_size="512x512",
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(
            lambda self: OpenAiImageQueryDriver(
                model="gpt-4o", api_key=self.api_key, base_url=self.base_url, organization=self.organization
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: OpenAiEmbeddingDriver(
                model="text-embedding-3-small",
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda self: LocalVectorStoreDriver(
                embedding_driver=OpenAiEmbeddingDriver(
                    model="text-embedding-3-small",
                    api_key=self.api_key,
                    base_url=self.base_url,
                    organization=self.organization,
                )
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
