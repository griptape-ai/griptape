from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from attr import define, field
from griptape.utils.text import to_vector_index
from griptape.utils import J2
from griptape.drivers import BasePromptDriver
from griptape.summarizers.base_summarizer import BaseSummarizer

if TYPE_CHECKING:
    from griptape.memory import Run


@define
class PromptDriverSummarizer(BaseSummarizer):
    driver: BasePromptDriver = field(kw_only=True)

    def summarize_runs(self, previous_summary: str, runs: list[Run]) -> str:
        try:
            if len(runs) > 0:
                return self.driver.run(
                    value=J2("prompts/summarize.j2").render(
                        summary=previous_summary,
                        runs=runs
                    )
                ).value
            else:
                return previous_summary
        except Exception as e:
            logging.error(f"Error summarizing memory: {type(e).__name__}({e})")

            return previous_summary

    def summarize_text(self, text: str) -> str:
        return str(
            to_vector_index(text).query(
                "Generate a summary. Include URLs in the summary."
            )
        ).strip()
