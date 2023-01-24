from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.drivers import CompletionDriver
from galaxybrain.summarizers.summarizer import Summarizer
from galaxybrain.prompts import Prompt


if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Memory


@define
class CompletionDriverSummarizer(Summarizer):
    driver: CompletionDriver = field(kw_only=True)

    def summarize(self, memory: Memory, steps: list[Step]) -> Optional[str]:
        if len(steps) > 0:
            return self.driver.run(
                value=Prompt.summarize(memory.summary, steps)
            ).value
        else:
            return memory.summary
