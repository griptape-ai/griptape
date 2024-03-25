from attrs import Factory, define, field

from griptape.config import (
    BaseStructureConfig,
    StructureGlobalDriversConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemoryExtractionEngineCsvConfig,
    StructureTaskMemoryExtractionEngineJsonConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
)
from griptape.drivers import LocalVectorStoreDriver


@define
class StructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(lambda: StructureGlobalDriversConfig()), kw_only=True, metadata={"serializable": True}
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(
            lambda self: StructureTaskMemoryConfig(
                query_engine=StructureTaskMemoryQueryEngineConfig(
                    prompt_driver=self.global_drivers.prompt_driver,
                    vector_store_driver=LocalVectorStoreDriver(embedding_driver=self.global_drivers.embedding_driver),
                ),
                extraction_engine=StructureTaskMemoryExtractionEngineConfig(
                    csv=StructureTaskMemoryExtractionEngineCsvConfig(prompt_driver=self.global_drivers.prompt_driver),
                    json=StructureTaskMemoryExtractionEngineJsonConfig(prompt_driver=self.global_drivers.prompt_driver),
                ),
                summary_engine=StructureTaskMemorySummaryEngineConfig(prompt_driver=self.global_drivers.prompt_driver),
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
