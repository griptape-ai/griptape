from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Optional, cast

from attrs import Factory, define, field

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack
from griptape.common.prompt_stack.messages.message import Message
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.rules import Ruleset


@define
class JsonExtractionEngine(BaseExtractionEngine):
    JSON_PATTERN = r"(?s)[^\[]*(\[.*\])"

    system_template_generator: J2 = field(
        default=Factory(lambda: J2("engines/json_extraction/system.j2")), kw_only=True
    )
    user_template_generator: J2 = field(default=Factory(lambda: J2("engines/json_extraction/user.j2")), kw_only=True)

    def extract_artifacts(
        self,
        artifacts: ListArtifact,
        *,
        rulesets: Optional[list[Ruleset]] = None,
        template_schema: Optional[list[dict]] = None,
        **kwargs,
    ) -> ListArtifact | ErrorArtifact:
        if template_schema is None:
            template_schema = []
        try:
            json_schema = json.dumps(template_schema)

            return ListArtifact(
                self._extract_rec(
                    cast(list[TextArtifact], artifacts.value),
                    json_schema,
                    [],
                    rulesets=rulesets,
                ),
                item_separator="\n",
            )
        except Exception as e:
            return ErrorArtifact(f"error extracting JSON: {e}")

    def json_to_text_artifacts(self, json_input: str) -> list[TextArtifact]:
        json_matches = re.findall(self.JSON_PATTERN, json_input, re.DOTALL)

        if json_matches:
            return [TextArtifact(json.dumps(e)) for e in json.loads(json_matches[-1])]
        else:
            return []

    def _extract_rec(
        self,
        artifacts: list[TextArtifact],
        json_template_schema: str,
        extractions: list[TextArtifact],
        rulesets: Optional[list[Ruleset]] = None,
    ) -> list[TextArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        system_prompt = self.system_template_generator.render(
            json_template_schema=json_template_schema,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )
        user_prompt = self.user_template_generator.render(
            text=artifacts_text,
        )

        if (
            self.prompt_driver.tokenizer.count_input_tokens_left(user_prompt + system_prompt)
            >= self.min_response_tokens
        ):
            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(
                            messages=[
                                Message(system_prompt, role=Message.SYSTEM_ROLE),
                                Message(user_prompt, role=Message.USER_ROLE),
                            ]
                        )
                    ).value
                ),
            )

            return extractions
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.user_template_generator.render(
                text=chunks[0].value,
            )

            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(
                            messages=[
                                Message(system_prompt, role=Message.SYSTEM_ROLE),
                                Message(partial_text, role=Message.USER_ROLE),
                            ]
                        )
                    ).value,
                ),
            )

            return self._extract_rec(chunks[1:], json_template_schema, extractions, rulesets=rulesets)
