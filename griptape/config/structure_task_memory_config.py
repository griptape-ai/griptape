from attrs import define, field

from griptape.config import (
    StructureTaskMemoryQueryEngineConfig,
    StructureTaskMemoryExtractionEngineConfig,
    StructureTaskMemorySummaryEngineConfig,
)


@define(kw_only=True)
class StructureTaskMemoryConfig:
    query_engine: StructureTaskMemoryQueryEngineConfig = field()
    extraction_engine: StructureTaskMemoryExtractionEngineConfig = field()
    summary_engine: StructureTaskMemorySummaryEngineConfig = field()
