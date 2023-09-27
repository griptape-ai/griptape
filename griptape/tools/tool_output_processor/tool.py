from __future__ import annotations
from typing import Optional
from attr import define
from griptape.memory.tool import TextToolMemory
from griptape.mixins import TextMemoryActivitiesMixin
from griptape.tools import BaseTool


@define
class ToolOutputProcessor(BaseTool, TextMemoryActivitiesMixin):
    def find_input_memory(self, memory_name: str) -> Optional[TextToolMemory]:
        """
        Override parent method to only return TextToolMemory
        """
        if self.input_memory:
            return next((m for m in self.input_memory if isinstance(m, TextToolMemory) and m.name == memory_name), None)
        else:
            return None