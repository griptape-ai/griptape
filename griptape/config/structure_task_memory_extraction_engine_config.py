from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

from .structure_task_memory_extraction_engine_csv_config import StructureTaskMemoryExtractionEngineCsvConfig
from .structure_task_memory_extraction_engine_json_config import StructureTaskMemoryExtractionEngineJsonConfig


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineConfig(SerializableMixin):
    csv: StructureTaskMemoryExtractionEngineCsvConfig = field(metadata={"save": True})
    json: StructureTaskMemoryExtractionEngineJsonConfig = field(metadata={"save": True})
