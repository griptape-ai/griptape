from typing import Optional, Union
from attr import field, define, Factory
from griptape.artifacts import ListArtifact, TextArtifact
from griptape.chunkers import TextChunker
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader
from griptape.tokenizers import TiktokenTokenizer


@define
class TextLoader(BaseLoader):
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda: TiktokenTokenizer()),
        kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.max_tokens, takes_self=True),
        kw_only=True
    )
    chunker: TextChunker = field(
        default=Factory(
            lambda self: TextChunker(
                tokenizer=self.tokenizer,
                max_tokens=self.max_tokens
            ),
            takes_self=True
        ),
        kw_only=True
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, text: str) -> Union[TextArtifact, ListArtifact]:
        return self.text_to_artifact(text)

    def text_to_artifact(self, text: str) -> Union[TextArtifact, ListArtifact]:
        if self.chunker:
            chunks = self.chunker.chunk(text)
        else:
            chunks = [TextArtifact(text)]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        if len(chunks) > 1:
            list_artifact = ListArtifact()

            for chunk in chunks:
                list_artifact.value.append(chunk)

            return list_artifact
        else:
            return chunks[0]
