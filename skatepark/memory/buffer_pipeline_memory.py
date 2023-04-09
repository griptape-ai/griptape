from __future__ import annotations
import json
from attr import define, field
from skatepark.memory import PipelineMemory, PipelineRun


@define
class BufferPipelineMemory(PipelineMemory):
    buffer_size: int = field(default=1, kw_only=True)

    def process_add_run(self, run: PipelineRun) -> None:
        super().process_add_run(run)

        while len(self.runs) > self.buffer_size:
            self.runs.pop(0)

    def to_dict(self) -> dict:
        return BufferPipelineMemory().dump(self)

    @classmethod
    def from_dict(cls, memory_dict: dict) -> PipelineMemory:
        return BufferPipelineMemory().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> PipelineMemory:
        return BufferPipelineMemory.from_dict(json.loads(memory_json))
