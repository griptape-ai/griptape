from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.drivers import CompletionDriver
from galaxybrain.summarizers.summarizer import Summarizer


if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Memory


@define
class CompletionDriverSummarizer(Summarizer):
    driver: CompletionDriver = field(kw_only=True)

    def summarize(self, memory: Memory, steps: list[Step]) -> Optional[str]:
        if len(steps) > 0:
            return self.driver.run(
                value=J2("summarize.j2").render(
                    summary=memory.summary,
                    steps=steps
                )
            ).value
        else:
            return memory.summary
