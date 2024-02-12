from attrs import Factory, define, field

from griptape.drivers import (
    BasePromptDriver,
    BaseVectorStoreDriver,
    NopVectorStoreDriver,
    NopEmbeddingDriver,
    NopPromptDriver,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryQueryEngineConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: NopPromptDriver()), metadata={"serializable": True}
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        kw_only=True,
        default=Factory(lambda: NopVectorStoreDriver(embedding_driver=NopEmbeddingDriver())),
        metadata={"serializable": True},
    )
