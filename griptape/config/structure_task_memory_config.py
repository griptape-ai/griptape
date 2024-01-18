from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

from .structure_task_memory_query_engine_config import StructureTaskMemoryQueryEngineConfig
from .structure_task_memory_extraction_engine_config import StructureTaskMemoryExtractionEngineConfig
from .structure_task_memory_summary_engine_config import StructureTaskMemorySummaryEngineConfig


@define(kw_only=True)
class StructureTaskMemoryConfig(SerializableMixin):
    query_engine: StructureTaskMemoryQueryEngineConfig = field(metadata={"serializable": True})
    extraction_engine: StructureTaskMemoryExtractionEngineConfig = field(metadata={"serializable": True})
    summary_engine: StructureTaskMemorySummaryEngineConfig = field(metadata={"serializable": True})
