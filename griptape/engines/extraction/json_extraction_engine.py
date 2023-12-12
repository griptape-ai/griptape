from __future__ import annotations
from typing import Optional
import json
from attr import field, Factory, define
from griptape.artifacts import TextArtifact, ListArtifact, ErrorArtifact
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2
from griptape.utils import PromptStack
from griptape.rules import Ruleset, rule


@define
class JsonExtractionEngine(BaseExtractionEngine):
    template_generator: J2 = field(default=Factory(lambda: J2("engines/extraction/json_extraction.j2")), kw_only=True)

    def extract(
        self, text: str | ListArtifact, template_schema: dict, rulesets: Ruleset | None = None
    ) -> ListArtifact | ErrorArtifact:
        try:
            json_schema = json.dumps(template_schema)

            return ListArtifact(
                self._extract_rec(
                    text.value if isinstance(text, ListArtifact) else [TextArtifact(text)],
                    json_schema,
                    [],
                    rulesets=rulesets,
                ),
                item_separator="\n",
            )
        except Exception as e:
            return ErrorArtifact(f"error extracting JSON: {e}")

    def json_to_text_artifacts(self, json_input: str) -> list[TextArtifact]:
        return [TextArtifact(e) for e in json.loads(json_input)]

    def _extract_rec(
        self,
        artifacts: list[TextArtifact],
        json_template_schema: str,
        extractions: list[TextArtifact],
        rulesets: Ruleset | None = None,
    ) -> list[TextArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        full_text = self.template_generator.render(
            json_template_schema=json_template_schema,
            text=artifacts_text,
            rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
        )

        if self.prompt_driver.tokenizer.count_tokens_left(full_text) >= self.min_response_tokens:
            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(inputs=[PromptStack.Input(full_text, role=PromptStack.USER_ROLE)])
                    ).value
                )
            )

            return extractions
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.template_generator.render(
                template_schema=json_template_schema,
                text=chunks[0].value,
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
            )

            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(inputs=[PromptStack.Input(partial_text, role=PromptStack.USER_ROLE)])
                    ).value
                )
            )

            return self._extract_rec(chunks[1:], json_template_schema, extractions, rulesets=rulesets)
