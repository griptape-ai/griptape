from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from attr import define, field
from llama_index import Document, GPTListIndex
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
        index = GPTListIndex.from_documents([Document(text)])
        query_engine = index.as_query_engine(
            response_mode="tree_summarize"
        )

        return str(
            query_engine.query(
                "Generate a summary. Include URLs in the summary."
            )
        ).strip()
