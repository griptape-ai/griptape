from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.utils import J2
from griptape.drivers import BasePromptDriver
from griptape.summarizers.summarizer import Summarizer


if TYPE_CHECKING:
    from griptape.memory import Run


@define
class PromptDriverSummarizer(Summarizer):
    driver: BasePromptDriver = field(kw_only=True)

    def summarize(self, summary: str, runs: list[Run]) -> Optional[str]:
        try:
            if len(runs) > 0:
                return self.driver.run(
                    value=J2("prompts/summarize.j2").render(
                        summary=summary,
                        runs=runs
                    )
                ).value
            else:
                return summary
        except Exception as e:
            self.pipeline.logger.error(f"Error summarizing memory: {type(e).__name__}({e})")

            return summary
