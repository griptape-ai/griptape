from attrs import Factory, define, field

from griptape.config import StructureTaskMemoryExtractionEngineCsvConfig, StructureTaskMemoryExtractionEngineJsonConfig
from griptape.mixins.serializable_mixin import SerializableMixin


@define
class StructureTaskMemoryExtractionEngineConfig(SerializableMixin):
    csv: StructureTaskMemoryExtractionEngineCsvConfig = field(
        kw_only=True,
        default=Factory(lambda: StructureTaskMemoryExtractionEngineCsvConfig()),
        metadata={"serializable": True},
    )
    json: StructureTaskMemoryExtractionEngineJsonConfig = field(
        kw_only=True,
        default=Factory(lambda: StructureTaskMemoryExtractionEngineJsonConfig()),
        metadata={"serializable": True},
    )
