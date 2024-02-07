from attrs import Factory, define, field

from griptape.config import (
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class StructureTaskMemoryConfig(SerializableMixin):
    query_engine: StructureTaskMemoryQueryEngineConfig = field(
        default=Factory(lambda: StructureTaskMemoryQueryEngineConfig()), metadata={"serializable": True}
    )
    extraction_engine: StructureTaskMemoryExtractionEngineConfig = field(
        default=Factory(lambda: StructureTaskMemoryExtractionEngineConfig()), metadata={"serializable": True}
    )
    summary_engine: StructureTaskMemorySummaryEngineConfig = field(
        default=Factory(lambda: StructureTaskMemorySummaryEngineConfig()), metadata={"serializable": True}
    )
