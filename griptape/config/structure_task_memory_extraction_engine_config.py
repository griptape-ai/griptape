from attrs import Factory, define, field

from griptape.config import StructureTaskMemoryExtractionEngineCsvConfig, StructureTaskMemoryExtractionEngineJsonConfig
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class StructureTaskMemoryExtractionEngineConfig(SerializableMixin):
    csv: StructureTaskMemoryExtractionEngineCsvConfig = field(
        default=Factory(lambda: StructureTaskMemoryExtractionEngineCsvConfig()), metadata={"serializable": True}
    )
    json: StructureTaskMemoryExtractionEngineJsonConfig = field(
        default=Factory(lambda: StructureTaskMemoryExtractionEngineJsonConfig()), metadata={"serializable": True}
    )
