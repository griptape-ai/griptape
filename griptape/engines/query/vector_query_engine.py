from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact
from griptape.utils import PromptStack
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import BaseQueryEngine
from griptape.utils.j2 import J2
from griptape.tokenizers import OpenAiTokenizer

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver


@define
class VectorQueryEngine(BaseQueryEngine):
    answer_token_offset: int = field(default=400, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    template_generator: J2 = field(default=Factory(lambda: J2("engines/query/vector_query.j2")), kw_only=True)

    def query(
        self,
        query: str,
        metadata: str | None = None,
        top_n: int | None = None,
        namespace: str | None = None,
        rulesets: str | None = None,
    ) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        result = self.vector_store_driver.query(query, top_n, namespace)
        artifacts = [
            a for a in [BaseArtifact.from_json(r.meta["artifact"]) for r in result] if isinstance(a, TextArtifact)
        ]
        text_segments = []
        message = ""

        for artifact in artifacts:
            text_segments.append(artifact.value)

            message = self.template_generator.render(
                metadata=metadata,
                query=query,
                text_segments=text_segments,
                rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
            )
            message_token_count = self.prompt_driver.token_count(
                PromptStack(inputs=[PromptStack.Input(message, role=PromptStack.USER_ROLE)])
            )

            if message_token_count + self.answer_token_offset >= tokenizer.max_tokens:
                text_segments.pop()

                message = self.template_generator.render(
                    metadata=metadata,
                    query=query,
                    text_segments=text_segments,
                    rulesets=J2("rulesets/rulesets.j2").render(rulesets=rulesets),
                )

                break

        return self.prompt_driver.run(PromptStack(inputs=[PromptStack.Input(message, role=PromptStack.USER_ROLE)]))

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: str | None = None) -> str:
        result = self.vector_store_driver.upsert_text_artifact(artifact, namespace=namespace)

        return result

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: str) -> None:
        self.vector_store_driver.upsert_text_artifacts({namespace: artifacts})

    def load_artifacts(self, namespace: str) -> ListArtifact:
        result = self.vector_store_driver.load_entries(namespace)
        artifacts = [BaseArtifact.from_json(r.meta["artifact"]) for r in result if r.meta.get("artifact")]

        return ListArtifact([a for a in artifacts if isinstance(a, TextArtifact)])
