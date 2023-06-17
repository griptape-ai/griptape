from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import BaseVectorStoreDriver, LocalVectorStoreDriver, BasePromptDriver, OpenAiPromptDriver
from griptape.engines import BaseQueryEngine


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

    def query(
            self,
            query: str,
            top_n: Optional[int] = None,
            namespace: Optional[str] = None
    ) -> TextArtifact:
        tokenizer = self.prompt_driver.tokenizer
        result = self.vector_store_driver.query(query, top_n, namespace)
        artifacts = [
            a for a in [BaseArtifact.from_json(r.meta["artifact"]) for r in result] if isinstance(a, TextArtifact)
        ]

        prefix_list = [
            "You are a helpful assistant who can answer questions by searching through text segments.",
            "Always be thruthful. Don't make up facts.",
            "Use the below list of text segments to answer the subsequent question.",
            'If the answer cannot be found in the segments, say "I could not find an answer."'
        ]

        prefix = " ".join(prefix_list)
        question = f"\n\nQuestion: {query}"

        for artifact in artifacts:
            next_segment = f'\n\nText segment:\n"""\n{artifact.value_and_meta}\n"""'

            if tokenizer.token_count(prefix + next_segment + question) > tokenizer.max_tokens:
                break
            else:
                prefix += next_segment

        return self.prompt_driver.run(value=prefix + question)
