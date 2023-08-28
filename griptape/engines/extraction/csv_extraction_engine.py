import csv
import io
from attr import field, Factory, define
from griptape.artifacts import TextArtifact, CsvRowArtifact
from griptape.chunkers import BaseChunker, TextChunker
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2


@define
class CsvExtractionEngine(BaseExtractionEngine):
    chunk_joiner: str = field(
        default="\n\n",
        kw_only=True
    )
    template_generator: J2 = field(
        default=Factory(lambda: J2("engines/csv_extraction.j2")),
        kw_only=True
    )
    max_token_multiplier: float = field(
        default=0.5,
        kw_only=True
    )
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver()),
        kw_only=True
    )
    chunker: BaseChunker = field(
        default=Factory(lambda self: TextChunker(
            tokenizer=self.prompt_driver.tokenizer,
            max_tokens=self.max_chunker_tokens
        ), takes_self=True),
        kw_only=True
    )

    @max_token_multiplier.validator
    def validate_allowlist(self, _, max_token_multiplier: int) -> None:
        if max_token_multiplier > 1:
            raise ValueError("has to be less than or equal to 1")
        elif max_token_multiplier <= 0:
            raise ValueError("has to be greater than 0")

    @property
    def max_chunker_tokens(self) -> int:
        return round(self.prompt_driver.tokenizer.max_tokens * self.max_token_multiplier)

    @property
    def min_response_tokens(self) -> int:
        return round(
            self.prompt_driver.tokenizer.max_tokens -
            self.prompt_driver.tokenizer.max_tokens *
            self.max_token_multiplier
        )

    def extract(self, artifacts: list[TextArtifact], column_names: list[str]) -> list[CsvRowArtifact]:
        return self.extract_rec(artifacts, column_names, [])

    def extract_rec(
            self,
            artifacts: list[TextArtifact],
            column_names: list[str],
            rows: list[CsvRowArtifact]
    ) -> list[CsvRowArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        full_text = self.template_generator.render(
            column_names=column_names,
            text=artifacts_text
        )

        if self.prompt_driver.tokenizer.tokens_left(full_text) >= self.min_response_tokens:
            rows.extend(
                self.text_to_csv_rows(
                    column_names,
                    self.prompt_driver.run(
                        PromptStack(
                            inputs=[PromptStack.Input(full_text, role=PromptStack.USER_ROLE)]
                        )
                    ).value
                )
            )

            return rows
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.template_generator.render(
                column_names=column_names,
                text=chunks[0].value
            )

            rows.extend(
                self.text_to_csv_rows(
                    column_names,
                    self.prompt_driver.run(
                        PromptStack(
                            inputs=[PromptStack.Input(partial_text, role=PromptStack.USER_ROLE)]
                        )
                    ).value
                )
            )

            return self.extract_rec(
                chunks[1:],
                column_names,
                rows
            )

    def text_to_csv_rows(self, column_names: list[str], text: str) -> list[CsvRowArtifact]:
        rows = []

        with io.StringIO(text) as f:
            for row in csv.reader(f):
                rows.append(
                    CsvRowArtifact(
                        dict(zip(column_names, [x.strip() for x in row]))
                    )
                )

        return rows
