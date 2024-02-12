from attrs import Factory, define, field

from griptape.drivers import (
    BasePromptDriver,
    BaseVectorStoreDriver,
    DummyVectorStoreDriver,
    DummyEmbeddingDriver,
    DummyPromptDriver,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryQueryEngineConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(
        kw_only=True, default=Factory(lambda: DummyPromptDriver()), metadata={"serializable": True}
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        kw_only=True,
        default=Factory(lambda: DummyVectorStoreDriver(embedding_driver=DummyEmbeddingDriver())),
        metadata={"serializable": True},
    )
