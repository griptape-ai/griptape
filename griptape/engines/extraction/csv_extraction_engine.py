from __future__ import annotations
from typing import Optional
import csv
import io
from attr import field, Factory, define
from griptape.artifacts import TextArtifact, CsvRowArtifact, ListArtifact, ErrorArtifact
from griptape.utils import PromptStack
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2
from griptape.rules import Ruleset, rule


@define
class CsvExtractionEngine(BaseExtractionEngine):
    template_generator: J2 = field(default=Factory(lambda: J2("engines/extraction/csv_extraction.j2")), kw_only=True)

    def extract(
        self, text: str | ListArtifact, column_names: list[str], rulesets: Ruleset | None = None
    ) -> ListArtifact | ErrorArtifact:
        try:
            return ListArtifact(
                self._extract_rec(
                    text.value if isinstance(text, ListArtifact) else [TextArtifact(text)],
                    column_names,
                    [],
                    rulesets=rulesets,
                ),
                item_separator="\n",
            )
        except Exception as e:
            return ErrorArtifact(f"error extracting CSV rows: {e}")

    def text_to_csv_rows(self, text: str, column_names: list[str]) -> list[CsvRowArtifact]:
        rows = []

        with io.StringIO(text) as f:
            for row in csv.reader(f):
                rows.append(CsvRowArtifact(dict(zip(column_names, [x.strip() for x in row]))))

        return rows

    def _extract_rec(
        self,
        artifacts: list[TextArtifact],
        column_names: list[str],
        rows: list[CsvRowArtifact],
        rulesets: Ruleset | None = None,
    ) -> list[CsvRowArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        full_text = self.template_generator.render(
            column_names=column_names,
            text=artifacts_text,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )

        if self.prompt_driver.tokenizer.count_tokens_left(full_text) >= self.min_response_tokens:
            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(
                        PromptStack(inputs=[PromptStack.Input(full_text, role=PromptStack.USER_ROLE)])
                    ).value,
                    column_names,
                )
            )

            return rows
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.template_generator.render(
                column_names=column_names,
                text=chunks[0].value,
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
            )

            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(
                        PromptStack(inputs=[PromptStack.Input(partial_text, role=PromptStack.USER_ROLE)])
                    ).value,
                    column_names,
                )
            )

            return self._extract_rec(chunks[1:], column_names, rows, rulesets=rulesets)
