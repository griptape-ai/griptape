from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import BaseVectorStoreDriver, LocalVectorStoreDriver, BasePromptDriver, OpenAiPromptDriver
from griptape.engines import BaseQueryEngine
from griptape.utils.j2 import J2


@define
class VectorQueryEngine(BaseQueryEngine):
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda: LocalVectorStoreDriver()),
        kw_only=True
    )
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiPromptDriver()),
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

        for artifact in artifacts:
            text_segments.append(artifact.value)

            message = self.template_generator.render(
                metadata=metadata,
                question=query,
                text_segments=text_segments,
            )

            if tokenizer.token_count(message) > tokenizer.max_tokens:
                text_segments.pop()
                break

        message = self.template_generator.render(
            metadata=metadata,
            question=query,
            text_segments=text_segments,
        )
        return self.prompt_driver.run(value=message)

    def upsert_text_artifact(
            self,
            artifact: TextArtifact,
            namespace: Optional[str] = None
    ) -> str:
        result = self.vector_store_driver.upsert_text_artifact(
            artifact,
            namespace=namespace
        )

        return result

    def upsert_text_artifacts(
            self,
            artifacts: list[TextArtifact],
            namespace: str
    ) -> None:
        self.vector_store_driver.upsert_text_artifacts({
            namespace: artifacts
        })
