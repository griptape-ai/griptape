from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.drivers import PromptDriver
from galaxybrain.summarizers.summarizer import Summarizer


if TYPE_CHECKING:
    from galaxybrain.steps import Step
    from galaxybrain.memory import Memory


@define
class CompletionDriverSummarizer(Summarizer):
    driver: PromptDriver = field(kw_only=True)

    def summarize(self, memory: Memory, steps: list[Step]) -> Optional[str]:
        if len(steps) > 0:
            return self.driver.run(
                value=J2("prompts/summarize.j2").render(
                    summary=memory.summary,
                    steps=steps
                )
            ).value
        else:
            return memory.summary
