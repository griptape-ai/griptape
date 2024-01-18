from attrs import define, field

from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class StructureTaskMemoryQueryEngineConfig(SerializableMixin):
    prompt_driver: BasePromptDriver = field(metadata={"serializable": True})
    vector_store_driver: BaseVectorStoreDriver = field(metadata={"serializable": True})
