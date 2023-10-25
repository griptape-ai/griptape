from typing import Optional
from attr import define, field, Factory
from griptape.memory import ToolMemory
from griptape.mixins import ToolMemoryActivitiesMixin
from tests.utils import defaults


@define
class MockToolMemoryProcessor(ToolMemoryActivitiesMixin):
    memory: ToolMemory = field(
        default=Factory(lambda: defaults.text_tool_memory("TestMemory"))
    )

    def find_input_memory(self, memory_name: str) -> Optional[ToolMemory]:
        return self.memory
