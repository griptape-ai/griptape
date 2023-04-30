from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from attr import define, field
from griptape.utils import J2
from griptape.drivers import BasePromptDriver
from griptape.summarizers.base_summarizer import BaseSummarizer

if TYPE_CHECKING:
    from griptape.memory import Run
    from llama_index import GPTSimpleVectorIndex


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
        index = self._to_vector_index(text)

        return str(index.query("What is the summary of the following text? Include links.")).strip()

    def _to_vector_index(self, text: str) -> GPTSimpleVectorIndex:
        from llama_index import GPTSimpleVectorIndex, Document

        return GPTSimpleVectorIndex([
            Document(text)
        ])
