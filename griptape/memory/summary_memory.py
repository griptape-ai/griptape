from __future__ import annotations
import json
from typing import TYPE_CHECKING
from typing import Optional
from attr import define, field
from griptape.utils import J2
from griptape.memory import Memory

if TYPE_CHECKING:
    from griptape.summarizers import BaseSummarizer
    from griptape.memory import Run


@define
class SummaryMemory(Memory):
    offset: int = field(default=1, kw_only=True)
    summarizer: Optional[BaseSummarizer] = field(default=None, kw_only=True)
    summary: Optional[str] = field(default=None, kw_only=True)
    summary_index: int = field(default=0, kw_only=True)

    def unsummarized_runs(self, last_n: Optional[int] = None) -> list[Run]:
        summary_index_runs = self.runs[self.summary_index:]

        if last_n:
            last_n_runs = self.runs[-last_n:]

            if len(summary_index_runs) > len(last_n_runs):
                return last_n_runs
            else:
                return summary_index_runs
        else:
            return summary_index_runs

    def process_add_run(self, run: Run) -> None:
        super().process_add_run(run)

        if self.summarizer:
            unsummarized_runs = self.unsummarized_runs()
            runs_to_summarize = unsummarized_runs[:max(0, len(unsummarized_runs) - self.offset)]

            if len(runs_to_summarize) > 0:
                self.summary = self.summarizer.summarize_runs(self.summary, runs_to_summarize)
                self.summary_index = 1 + self.runs.index(runs_to_summarize[-1])

    def to_prompt_string(self, last_n: Optional[int] = None):
        return J2("prompts/memory.j2").render(
            summary=self.summary,
            runs=self.unsummarized_runs(last_n)
        )

    def to_dict(self) -> dict:
        return SummaryMemory().dump(self)

    @classmethod
    def from_dict(cls, memory_dict: dict) -> Memory:
        return SummaryMemory().load(memory_dict)

    @classmethod
    def from_json(cls, memory_json: str) -> Memory:
        return SummaryMemory.from_dict(json.loads(memory_json))
