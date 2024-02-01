from attrs import define, field, Factory

from typing import Optional
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.drivers import (
    BasePromptDriver,
    BaseImageGenerationDriver,
    BaseEmbeddingDriver,
    BaseVectorStoreDriver,
    LocalVectorStoreDriver,
    BaseConversationMemoryDriver,
)


@define(kw_only=True)
class StructureGlobalDriversConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(kw_only=True, metadata={"serializable": True})
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True, metadata={"serializable": True})
    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding_driver), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
