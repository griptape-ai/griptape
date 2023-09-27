from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import abstractmethod
from attr import define

if TYPE_CHECKING:
    from griptape.memory.tool import BaseToolMemory
    from griptape.tools import BaseTool
    from griptape.tasks import ActionSubtask


@define(slots=False)
class ActionSubtaskOriginMixin:
    @property
    @abstractmethod
    def action_types(self) -> list[str]:
        ...

    @abstractmethod
    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        ...

    @abstractmethod
    def find_memory(self, memory_name: str) -> Optional[BaseToolMemory]:
        ...

    @abstractmethod
    def find_subtask(self, subtask_id: str) -> Optional[ActionSubtask]:
        ...

    @abstractmethod
    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        ...