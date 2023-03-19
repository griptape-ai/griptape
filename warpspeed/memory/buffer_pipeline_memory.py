from __future__ import annotations
from attrs import define, field
from warpspeed.memory import PipelineMemory, PipelineRun


@define
class BufferPipelineMemory(PipelineMemory):
    buffer_size: int = field(default=1, kw_only=True)

    def add_run(self, run: PipelineRun) -> PipelineRun:
        run = super().add_run(run)

        while len(self.runs) > self.buffer_size:
            self.runs.pop(0)

        return run
