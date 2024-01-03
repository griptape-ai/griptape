from attrs import define, field

from .structure_task_memory_extraction_engine_csv_config import StructureTaskMemoryExtractionEngineCsvConfig
from .structure_task_memory_extraction_engine_json_config import StructureTaskMemoryExtractionEngineJsonConfig


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineConfig:
    csv: StructureTaskMemoryExtractionEngineCsvConfig = field()
    json: StructureTaskMemoryExtractionEngineJsonConfig = field()
