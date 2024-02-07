from __future__ import annotations

from abc import ABC

from attr import define, field

from griptape.config import BaseConfig, StructureGlobalDriversConfig, StructureTaskMemoryConfig
from griptape.utils import dict_merge


@define
class BaseStructureConfig(BaseConfig, ABC):
    global_drivers: StructureGlobalDriversConfig = field(kw_only=True, metadata={"serializable": True})
    task_memory: StructureTaskMemoryConfig = field(kw_only=True, metadata={"serializable": True})

    def merge_config(self, config: dict) -> BaseStructureConfig:
        base_config = self.to_dict()
        merged_config = dict_merge(base_config, config)

        return BaseStructureConfig.from_dict(merged_config)
