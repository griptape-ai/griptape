from __future__ import annotations
import json
from attr import define, field
from griptape.memory import Memory, Run


@define
class BufferMemory(Memory):
    buffer_size: int = field(default=1, kw_only=True)

    def process_add_run(self, run: Run) -> None:
        super().process_add_run(run)

        while len(self.runs) > self.buffer_size:
            self.runs.pop(0)

    def to_dict(self) -> dict:
        return BufferMemory().dump(self)

    @classmethod
    def from_dict(cls, memory_dict: dict) -> Memory:
        return BufferMemory().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> Memory:
        return BufferMemory.from_dict(json.loads(memory_json))
