from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from attrs import Attribute, Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.chunkers import BaseChunker, TextChunker
from griptape.common import PromptStack
from griptape.common.prompt_stack.messages.message import Message
from griptape.engines import BaseSummaryEngine
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver
    from griptape.rules import Ruleset


@define
class PromptSummaryEngine(BaseSummaryEngine):
    chunk_joiner: str = field(default="\n\n", kw_only=True)
    max_token_multiplier: float = field(default=0.5, kw_only=True)
    system_template_generator: J2 = field(default=Factory(lambda: J2("engines/summary/system.j2")), kw_only=True)
    user_template_generator: J2 = field(default=Factory(lambda: J2("engines/summary/user.j2")), kw_only=True)
    prompt_driver: BasePromptDriver = field(kw_only=True)
    chunker: BaseChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.prompt_driver.tokenizer, max_tokens=self.max_chunker_tokens),
            takes_self=True,
        ),
        kw_only=True,
    )

    @max_token_multiplier.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_allowlist(self, _: Attribute, max_token_multiplier: int) -> None:
        if max_token_multiplier > 1:
            raise ValueError("has to be less than or equal to 1")
        elif max_token_multiplier <= 0:
            raise ValueError("has to be greater than 0")

    @property
    def max_chunker_tokens(self) -> int:
        return round(self.prompt_driver.tokenizer.max_input_tokens * self.max_token_multiplier)

    @property
    def min_response_tokens(self) -> int:
        return round(
            self.prompt_driver.tokenizer.max_input_tokens
            - self.prompt_driver.tokenizer.max_input_tokens * self.max_token_multiplier,
        )

    def summarize_artifacts(self, artifacts: ListArtifact, *, rulesets: Optional[list[Ruleset]] = None) -> TextArtifact:
        return self.summarize_artifacts_rec(cast(list[TextArtifact], artifacts.value), None, rulesets=rulesets)

    def summarize_artifacts_rec(
        self,
        artifacts: list[TextArtifact],
        summary: Optional[str] = None,
        rulesets: Optional[list[Ruleset]] = None,
    ) -> TextArtifact:
        artifacts_text = self.chunk_joiner.join([a.to_text() for a in artifacts])

        system_prompt = self.system_template_generator.render(
            summary=summary,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )

        user_prompt = self.user_template_generator.render(text=artifacts_text)

        if (
            self.prompt_driver.tokenizer.count_input_tokens_left(user_prompt + system_prompt)
            >= self.min_response_tokens
        ):
            result = self.prompt_driver.run(
                PromptStack(
                    messages=[
                        Message(system_prompt, role=Message.SYSTEM_ROLE),
                        Message(user_prompt, role=Message.USER_ROLE),
                    ],
                ),
            ).to_artifact()

            if isinstance(result, TextArtifact):
                return result
            else:
                raise ValueError("Prompt driver did not return a TextArtifact")
        else:
            chunks = self.chunker.chunk(artifacts_text)

            partial_text = self.user_template_generator.render(text=chunks[0].value)

            return self.summarize_artifacts_rec(
                chunks[1:],
                self.prompt_driver.run(
                    PromptStack(
                        messages=[
                            Message(system_prompt, role=Message.SYSTEM_ROLE),
                            Message(partial_text, role=Message.USER_ROLE),
                        ],
                    ),
                ).value,
                rulesets=rulesets,
            )
