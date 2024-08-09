from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, Optional, cast

from attrs import Factory, define, field

from griptape.artifacts import CsvRowArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.common import Message, PromptStack
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.rules import Ruleset


@define
class CsvExtractionEngine(BaseExtractionEngine):
    column_names: list[str] = field(default=Factory(list), kw_only=True)
    template_generator: J2 = field(default=Factory(lambda: J2("engines/extraction/csv_extraction.j2")), kw_only=True)

    def extract(
        self,
        text: str | ListArtifact,
        *,
        rulesets: Optional[list[Ruleset]] = None,
        **kwargs,
    ) -> ListArtifact | ErrorArtifact:
        try:
            return ListArtifact(
                self._extract_rec(
                    cast(list[TextArtifact], text.value) if isinstance(text, ListArtifact) else [TextArtifact(text)],
                    [],
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
        rows: list[CsvRowArtifact],
        *,
        rulesets: Optional[list[Ruleset]] = None,
    ) -> list[CsvRowArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        full_text = self.template_generator.render(
            text=artifacts_text,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )

        if self.prompt_driver.tokenizer.count_input_tokens_left(full_text) >= self.min_response_tokens:
            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(PromptStack(messages=[Message(full_text, role=Message.USER_ROLE)])).value,
                    self.column_names,
                ),
            )

            return rows
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.template_generator.render(
                column_names=self.column_names,
                text=chunks[0].value,
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
            )

            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(PromptStack(messages=[Message(partial_text, role=Message.USER_ROLE)])).value,
                    self.column_names,
                ),
            )

            return self._extract_rec(chunks[1:], rows, rulesets=rulesets)
