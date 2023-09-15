from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.utils import PromptStack
from griptape.drivers import BaseVectorStoreDriver, BasePromptDriver, OpenAiChatPromptDriver
from griptape.engines import BaseQueryEngine
from griptape.utils.j2 import J2


@define
class VectorQueryEngine(BaseQueryEngine):
    answer_token_offset: int = field(default=400, kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver()),
        kw_only=True
    )
    template_generator: J2 = field(
        default=Factory(lambda: J2("engines/vector_query.j2")),
        kw_only=True
    )

    def query(
            self,
            query: str,
            metadata: Optional[str] = None,
            top_n: Optional[int] = None,
            namespace: Optional[str] = None
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
            )
            message_token_count = self.prompt_driver.token_count(
                PromptStack(
                    inputs=[PromptStack.Input(message, role=PromptStack.USER_ROLE)]
                )
            )

            if message_token_count + self.answer_token_offset >= tokenizer.max_tokens:
                text_segments.pop()

                message = self.template_generator.render(
                    metadata=metadata,
                    query=query,
                    text_segments=text_segments,
                )

                break

        return self.prompt_driver.run(
            PromptStack(
                inputs=[PromptStack.Input(message, role=PromptStack.USER_ROLE)]
            )
        )

    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        result = self.vector_store_driver.upsert_text_artifact(
            artifact,
            namespace=namespace
        )

        return result

    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: str) -> None:
        self.vector_store_driver.upsert_text_artifacts({
            namespace: artifacts
        })
