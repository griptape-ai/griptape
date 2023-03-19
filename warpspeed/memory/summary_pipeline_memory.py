from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define, field
from warpspeed.utils import J2
from warpspeed.memory import PipelineMemory

if TYPE_CHECKING:
    from warpspeed.summarizers import Summarizer
    from warpspeed.memory import PipelineRun


@define
class SummaryPipelineMemory(PipelineMemory):
    offset: int = field(default=1, kw_only=True)
    summarizer: Summarizer = field(kw_only=True)
    summary_index: int = field(default=0, init=False)
    summary: Optional[str] = field(default=None, init=False)

    def unsummarized_runs(self) -> list[PipelineRun]:
        return self.runs[self.summary_index:]

    def add_run(self, run: PipelineRun) -> PipelineRun:
        run = super().add_run(run)

        unsummarized_runs = self.unsummarized_runs()
        runs_to_summarize = unsummarized_runs[:max(0, len(unsummarized_runs) - self.offset)]

        if len(runs_to_summarize) > 0:
            self.summary = self.summarizer.summarize(self, runs_to_summarize)
            self.summary_index = 1 + self.runs.index(runs_to_summarize[-1])

        return run

    def to_prompt_string(self):
        return J2("prompts/memory.j2").render(
            summary=self.summary,
            runs=self.unsummarized_runs()
        )
