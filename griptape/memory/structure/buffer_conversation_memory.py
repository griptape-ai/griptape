from __future__ import annotations
import json
from attr import define, field
from griptape.memory.structure import ConversationMemory, Run
from griptape.schemas import BufferConversationMemorySchema


@define
class BufferConversationMemory(ConversationMemory):
    buffer_size: int = field(default=1, kw_only=True)

    def try_add_run(self, run: Run) -> None:
        super().try_add_run(run)

        while len(self.runs) > self.buffer_size:
            self.runs.pop(0)

    def to_dict(self) -> dict:
        return dict(BufferConversationMemorySchema().dump(self))

    @classmethod
    def from_dict(cls, memory_dict: dict) -> BufferConversationMemory:
        return BufferConversationMemorySchema().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> BufferConversationMemory:
        return BufferConversationMemory.from_dict(json.loads(memory_json))
