from attrs import define, field

from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver


@define(kw_only=True)
class StructureTaskMemoryQueryEngineConfig:
    prompt_driver: BasePromptDriver = field()
    vector_store_driver: BaseVectorStoreDriver = field()
