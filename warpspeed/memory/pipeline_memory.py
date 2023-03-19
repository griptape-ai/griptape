from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from warpspeed.memory import PipelineRun
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.structures import Pipeline


@define
class PipelineMemory:
    runs: list[PipelineRun] = field(factory=list, init=False)
    pipeline: Pipeline = field(init=False)

    def add_run(self, run: PipelineRun) -> PipelineRun:
        self.runs.append(run)

        return run

    def is_empty(self) -> bool:
        return not self.runs

    def to_prompt_string(self) -> str:
        return J2("prompts/memory.j2").render(
            runs=self.runs
        )
