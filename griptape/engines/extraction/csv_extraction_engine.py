from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, Callable, Optional, cast

from attrs import Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.common import Message, PromptStack
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.rules import Ruleset


@define
class CsvExtractionEngine(BaseExtractionEngine):
    column_names: list[str] = field(kw_only=True)
    generate_system_template: J2 = field(default=Factory(lambda: J2("engines/extraction/csv/system.j2")), kw_only=True)
    generate_user_template: J2 = field(default=Factory(lambda: J2("engines/extraction/csv/user.j2")), kw_only=True)
    format_row: Callable[[dict], str] = field(
        default=lambda value: "\n".join(f"{key}: {val}" for key, val in value.items()), kw_only=True
    )

    def extract_artifacts(
        self,
        artifacts: ListArtifact[TextArtifact],
        *,
        rulesets: Optional[list[Ruleset]] = None,
        **kwargs,
    ) -> ListArtifact[TextArtifact]:
        return ListArtifact(
            self._extract_rec(
                cast(list[TextArtifact], artifacts.value),
                [],
                rulesets=rulesets,
            ),
            item_separator="\n",
        )

    def text_to_csv_rows(self, text: str, column_names: list[str]) -> list[TextArtifact]:
        rows = []

        with io.StringIO(text) as f:
            for row in csv.reader(f):
                rows.append(TextArtifact(self.format_row(dict(zip(column_names, [x.strip() for x in row])))))

        return rows

    def _extract_rec(
        self,
        artifacts: list[TextArtifact],
        rows: list[TextArtifact],
        *,
        rulesets: Optional[list[Ruleset]] = None,
    ) -> list[TextArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        system_prompt = self.generate_system_template.render(
            column_names=self.column_names,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )
        user_prompt = self.generate_user_template.render(
            text=artifacts_text,
        )

        if (
            self.prompt_driver.tokenizer.count_input_tokens_left(system_prompt + user_prompt)
            >= self.min_response_tokens
        ):
            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(
                        PromptStack(
                            messages=[
                                Message(system_prompt, role=Message.SYSTEM_ROLE),
                                Message(user_prompt, role=Message.USER_ROLE),
                            ]
                        )
                    ).value,
                    self.column_names,
                ),
            )

            return rows
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.generate_user_template.render(
                text=chunks[0].value,
            )

            rows.extend(
                self.text_to_csv_rows(
                    self.prompt_driver.run(
                        PromptStack(
                            messages=[
                                Message(system_prompt, role=Message.SYSTEM_ROLE),
                                Message(partial_text, role=Message.USER_ROLE),
                            ]
                        )
                    ).value,
                    self.column_names,
                ),
            )

            return self._extract_rec(chunks[1:], rows, rulesets=rulesets)
