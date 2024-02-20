from typing import Optional

from attrs import Factory, define, field

from griptape.drivers import (
    BaseConversationMemoryDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    DummyVectorStoreDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyPromptDriver,
    DummyImageQueryDriver,
    BaseImageQueryDriver,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureGlobalDriversConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: DummyPromptDriver()), metadata={"serializable": True}
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        kw_only=True, default=Factory(lambda: DummyImageGenerationDriver()), metadata={"serializable": True}
    )
    image_query_driver: BaseImageQueryDriver = field(
        kw_only=True, default=Factory(lambda: DummyImageQueryDriver()), metadata={"serializable": True}
    )
    embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=Factory(lambda: DummyEmbeddingDriver()), metadata={"serializable": True}
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda: DummyVectorStoreDriver()), kw_only=True, metadata={"serializable": True}
    )
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
