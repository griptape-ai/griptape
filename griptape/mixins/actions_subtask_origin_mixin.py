from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from griptape.memory import TaskMemory
    from griptape.tasks import BaseSubtask
    from griptape.tools import BaseTool


@define(slots=False)
class ActionsSubtaskOriginMixin:
    @abstractmethod
    def find_tool(self, tool_name: str) -> BaseTool: ...

    @abstractmethod
    def find_memory(self, memory_name: str) -> TaskMemory: ...

    @abstractmethod
    def find_subtask(self, subtask_id: str) -> BaseSubtask: ...

    @abstractmethod
    def add_subtask(self, subtask: BaseSubtask) -> BaseSubtask: ...
