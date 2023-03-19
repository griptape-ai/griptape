from __future__ import annotations
from attrs import define, field
from warpspeed.memory import PipelineRun
from warpspeed.utils import J2


@define
class PipelineMemory:
    runs: list[PipelineRun] = field(factory=list, init=False)

    def add_run(self, run: PipelineRun) -> PipelineRun:
        self.runs.append(run)

        return run

    def is_empty(self) -> bool:
        return not self.runs

    def to_prompt_string(self) -> str:
        return J2("prompts/memory.j2").render(
            runs=self.runs
        )
