from attrs import define, field

from griptape.config import StructureTaskMemoryExtractionEngineCsvConfig, StructureTaskMemoryExtractionEngineJsonConfig


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineConfig:
    csv: StructureTaskMemoryExtractionEngineCsvConfig = field()
    json: StructureTaskMemoryExtractionEngineJsonConfig = field()
