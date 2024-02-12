from typing import Optional

from attrs import Factory, define, field

from griptape.drivers import (
    BaseConversationMemoryDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    NopVectorStoreDriver,
    NopEmbeddingDriver,
    NopImageGenerationDriver,
    NopPromptDriver,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureGlobalDriversConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: NopPromptDriver()), metadata={"serializable": True}
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        kw_only=True, default=Factory(lambda: NopImageGenerationDriver()), metadata={"serializable": True}
    )
    embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=Factory(lambda: NopEmbeddingDriver()), metadata={"serializable": True}
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda: NopVectorStoreDriver()), kw_only=True, metadata={"serializable": True}
    )
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
