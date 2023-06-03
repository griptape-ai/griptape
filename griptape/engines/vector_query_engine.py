from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import BaseVectorDriver, MemoryVectorDriver, BasePromptDriver, OpenAiPromptDriver
from griptape.engines import BaseQueryEngine


@define
class VectorQueryEngine(BaseQueryEngine):
    vector_driver: BaseVectorDriver = field(
        default=Factory(lambda: MemoryVectorDriver()),
        kw_only=True
    )
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiPromptDriver()),
        kw_only=True
    )

    def insert(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> None:
        [self.vector_driver.upsert_text_artifact(a, namespace=namespace) for a in artifacts]

    def query(self, query: str, top_n: Optional[int] = None, namespace: Optional[str] = None) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        result = self.vector_driver.query(query, top_n, namespace)
        artifacts = [BaseArtifact.from_json(r.meta["artifact"]) for r in result]

        prefix = 'Use the below list of text segments to answer the subsequent question. ' \
                 'If the answer cannot be found in the segments, write "I could not find an answer."'
        question = f"\n\nQuestion: {query}"

        for artifact in artifacts:
            next_segment = f'\n\nText segment:\n"""\n{artifact.value}\n"""'

            if tokenizer.token_count(prefix + next_segment + question) > tokenizer.max_tokens:
                break
            else:
                prefix += next_segment

        return self.prompt_driver.run(value=prefix + question)
