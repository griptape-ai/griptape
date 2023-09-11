from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attr import define

if TYPE_CHECKING:
    from griptape.memory.tool import TextToolMemory
    from griptape.tools import BaseTool
    from griptape.tasks import ActionSubtask


@define
class ActionSubtaskOriginMixin(ABC):
    @property
    @abstractmethod
    def action_types(self) -> list[str]:
        ...

    @abstractmethod
    def find_tool(self, tool_name: str) -> Optional[BaseTool]:
        ...

    @abstractmethod
    def find_memory(self, memory_name: str) -> Optional[TextToolMemory]:
        ...

    @abstractmethod
    def find_subtask(self, subtask_id: str) -> Optional[ActionSubtask]:
        ...

    @abstractmethod
    def add_subtask(self, subtask: ActionSubtask) -> ActionSubtask:
        ...
