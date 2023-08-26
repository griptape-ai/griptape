from typing import Optional
from attr import define, Factory, field
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.chunkers import BaseChunker, TextChunker
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.engines import BaseSummaryEngine
from griptape.utils import J2


@define
class PromptSummaryEngine(BaseSummaryEngine):
    chunk_joiner: str = field(
        default="\n\n",
        kw_only=True
    )
    max_token_multiplier: float = field(
        default=0.5,
        kw_only=True
    )
    template_generator: J2 = field(
        default=Factory(lambda: J2("engines/prompt_summary.j2")),
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

    def summarize_artifacts(self, artifacts: list[BaseArtifact]) -> TextArtifact:
        return self.summarize_artifacts_rec(artifacts, None)

    def summarize_artifacts_rec(self, artifacts: list[BaseArtifact], summary: Optional[str]) -> TextArtifact:
        artifacts_text = self.chunk_joiner.join([a.to_text() for a in artifacts])

        full_text = self.template_generator.render(
            summary=summary,
            text=artifacts_text
        )

        if self.prompt_driver.tokenizer.tokens_left(full_text) >= self.min_response_tokens:
            return self.prompt_driver.run(
                PromptStack(
                    inputs=[PromptStack.Input(full_text, role=PromptStack.USER_ROLE)]
                )
            )
        else:
            chunks = self.chunker.chunk(artifacts_text)

            partial_text = self.template_generator.render(
                summary=summary,
                text=chunks[0].value
            )

            return self.summarize_artifacts_rec(
                chunks[1:],
                self.prompt_driver.run(
                    PromptStack(
                        inputs=[PromptStack.Input(partial_text, role=PromptStack.USER_ROLE)]
                    )
                ).value
            )
