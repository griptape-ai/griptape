from attrs import Factory, define, field

from griptape.config import BaseStructureConfig, StructureGlobalDriversConfig, StructureTaskMemoryConfig


@define(kw_only=True)
class StructureConfig(BaseStructureConfig):
    global_drivers: StructureGlobalDriversConfig = field(
        default=Factory(lambda: StructureGlobalDriversConfig()), kw_only=True, metadata={"serializable": True}
    )
    task_memory: StructureTaskMemoryConfig = field(
        default=Factory(lambda: StructureTaskMemoryConfig()), kw_only=True, metadata={"serializable": True}
    )
