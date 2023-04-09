from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from skatepark.utils import J2
from skatepark.drivers import PromptDriver
from skatepark.summarizers.summarizer import Summarizer


if TYPE_CHECKING:
    from skatepark.memory import PipelineMemory, PipelineRun


@define
class PromptDriverSummarizer(Summarizer):
    driver: PromptDriver = field(kw_only=True)

    def summarize(self, memory: PipelineMemory, runs: list[PipelineRun]) -> Optional[str]:
        try:
            if len(runs) > 0:
                return self.driver.run(
                    value=J2("prompts/summarize.j2").render(
                        summary=memory.summary,
                        runs=runs
                    )
                ).value
            else:
                return memory.summary
        except Exception as e:
            self.pipeline.logger.error(f"Error summarizing memory: {type(e).__name__}({e})")

            return memory.summary
