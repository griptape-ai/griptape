from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import BaseVectorStorageDriver, MemoryVectorStorageDriver
from griptape.engines import BaseEngine


@define
class QueryEngine(BaseEngine):
    vector_storage_driver: BaseVectorStorageDriver = field(default=MemoryVectorStorageDriver(), kw_only=True)

    def insert(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> None:
        [self.vector_storage_driver.insert_text_artifact(a, namespace=namespace) for a in artifacts]

    def query(self, query: str, top_n: Optional[int] = None, namespace: Optional[str] = None) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        result = self.vector_storage_driver.query(query, top_n, namespace)
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
