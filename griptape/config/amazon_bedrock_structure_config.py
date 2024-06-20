from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional
from attrs import Factory, define, field

from griptape.drivers import BasePromptDriver
from griptape.utils import import_optional_dependency
from griptape.config import StructureConfig
from griptape.drivers import (
    AmazonBedrockImageGenerationDriver,
    AmazonBedrockImageQueryDriver,
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseVectorStoreDriver,
    BedrockClaudeImageQueryModelDriver,
    BedrockTitanImageGenerationModelDriver,
    LocalVectorStoreDriver,
)

if TYPE_CHECKING:
    import boto3


@define()
class AmazonBedrockStructureConfig(StructureConfig):
    region: Optional[str] = field(default=os.environ.get("AWS_DEFAULT_REGION", None), metadata={"serializable": True})
    access_key_id: Optional[str] = field(
        default=os.environ.get("AWS_ACCESS_KEY_ID", None), metadata={"serializable": False}
    )
    secret_access_key: Optional[str] = field(
        default=os.environ.get("AWS_SECRET_ACCESS_KEY", None), metadata={"serializable": False}
    )
    session: Optional[boto3.Session] = field(
        default=Factory(
            lambda self: import_optional_dependency("boto3").Session(
                region_name=self.region,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            ),
            takes_self=True,
        ),
        metadata={"serializable": False},
    )

    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: AmazonBedrockPromptDriver(
                session=self.session, model="anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: AmazonBedrockTitanEmbeddingDriver(session=self.session, model="amazon.titan-embed-text-v1"),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: AmazonBedrockImageGenerationDriver(
                session=self.session,
                model="amazon.titan-image-generator-v1",
                image_generation_model_driver=BedrockTitanImageGenerationModelDriver(),
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: AmazonBedrockImageQueryDriver(
                session=self.session,
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding_driver), takes_self=True),
        metadata={"serializable": True},
    )
