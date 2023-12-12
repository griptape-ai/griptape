from __future__ import annotations
from abc import ABC

from attr import define, field

from griptape.defaults import BaseDefaultsProvider
from griptape.drivers import BasePromptDriver
from griptape.memory import TaskMemory


@define
class BaseStructureDefaultsProvider(BaseDefaultsProvider, ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True)
    task_memory: TaskMemory = field(kw_only=True)
