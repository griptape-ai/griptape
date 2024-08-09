from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.config import DriverConfig
from griptape.drivers import (
    AmazonBedrockImageGenerationDriver,
    AmazonBedrockImageQueryDriver,
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    BedrockClaudeImageQueryModelDriver,
    BedrockTitanImageGenerationModelDriver,
    LocalVectorStoreDriver,
)
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define
class AmazonBedrockDriverConfig(DriverConfig):
    session: boto3.Session = field(
        default=Factory(lambda: import_optional_dependency("boto3").Session()),
        kw_only=True,
        metadata={"serializable": False},
    )

    prompt: BasePromptDriver = field(
        default=Factory(
            lambda self: AmazonBedrockPromptDriver(
                session=self.session,
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: AmazonBedrockTitanEmbeddingDriver(session=self.session, model="amazon.titan-embed-text-v1"),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_generation: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: AmazonBedrockImageGenerationDriver(
                session=self.session,
                model="amazon.titan-image-generator-v1",
                image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: AmazonBedrockImageQueryDriver(
                session=self.session,
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
                image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    vector_store: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
