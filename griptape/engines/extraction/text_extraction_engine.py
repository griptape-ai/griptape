import json
from attr import field, Factory, define
from griptape.artifacts import TextArtifact
from griptape.engines import BaseExtractionEngine
from griptape.utils import J2
from griptape.utils import PromptStack


@define
class TextExtractionEngine(BaseExtractionEngine):
    template_generator: J2 = field(
        default=Factory(lambda: J2("engines/extraction/text_extraction.j2")),
        kw_only=True
    )

    def extract(self, artifacts: list[TextArtifact], template_schema: str) -> list[TextArtifact]:
        assert json.loads(template_schema)

        return self._extract_rec(artifacts, template_schema, [])

    def json_to_text_artifacts(self, json_input: str) -> list[TextArtifact]:
        return [TextArtifact(e) for e in json.loads(json_input)]

    def _extract_rec(
            self,
            artifacts: list[TextArtifact],
            template_schema: str,
            extractions: list[TextArtifact]
    ) -> list[TextArtifact]:
        artifacts_text = self.chunk_joiner.join([a.value for a in artifacts])
        full_text = self.template_generator.render(
            template_schema=template_schema,
            text=artifacts_text
        )

        if self.prompt_driver.tokenizer.tokens_left(full_text) >= self.min_response_tokens:
            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(
                            inputs=[PromptStack.Input(full_text, role=PromptStack.USER_ROLE)]
                        )
                    ).value
                )
            )

            return extractions
        else:
            chunks = self.chunker.chunk(artifacts_text)
            partial_text = self.template_generator.render(
                template_schema=template_schema,
                text=chunks[0].value
            )

            extractions.extend(
                self.json_to_text_artifacts(
                    self.prompt_driver.run(
                        PromptStack(
                            inputs=[PromptStack.Input(partial_text, role=PromptStack.USER_ROLE)]
                        )
                    ).value
                )
            )

            return self._extract_rec(
                chunks[1:],
                template_schema,
                extractions
            )
