from attrs import Factory, define, field

from griptape.config import (
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
)
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryConfig(SerializableMixin):
    query_engine: StructureTaskMemoryQueryEngineConfig = field(
        kw_only=True, default=Factory(lambda: StructureTaskMemoryQueryEngineConfig()), metadata={"serializable": True}
    )
    extraction_engine: StructureTaskMemoryExtractionEngineConfig = field(
        kw_only=True,
        default=Factory(lambda: StructureTaskMemoryExtractionEngineConfig()),
        metadata={"serializable": True},
    )
    summary_engine: StructureTaskMemorySummaryEngineConfig = field(
        kw_only=True, default=Factory(lambda: StructureTaskMemorySummaryEngineConfig()), metadata={"serializable": True}
    )
