from attrs import define, field

from griptape.config import PromptDriverConfig, VectorStoreDriverConfig


@define(kw_only=True)
class StructureTaskMemoryQueryEngineConfig:
    prompt_driver: PromptDriverConfig = field()
    vector_store_driver: VectorStoreDriverConfig = field()
