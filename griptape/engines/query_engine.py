from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import BaseVectorStorageDriver, MemoryVectorStorageDriver
from griptape.engines import BaseEngine


@define
class QueryEngine(BaseEngine):
    vector_storage_driver: BaseVectorStorageDriver = field(default=MemoryVectorStorageDriver(), kw_only=True)
    top_n: Optional[int] = field(default=None, kw_only=True)

    def insert(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> None:
        [self.vector_storage_driver.insert_text_artifact(a, namespace=namespace) for a in artifacts]

    def query(self, query: str) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        artifacts = [
            BaseArtifact.from_json(r.meta["artifact"]) for r in self.vector_storage_driver.query(query, self.top_n)
        ]

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
