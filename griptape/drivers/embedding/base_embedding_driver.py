from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.mixins import ExponentialBackoffMixin
from griptape.tokenizers import BaseTokenizer
from griptape.chunkers import BaseChunker, TextChunker


@define
class BaseEmbeddingDriver(ExponentialBackoffMixin, ABC):
    """
    Attributes:
        tokenizer: An instance of `BaseTokenizer` to use when calculating tokens.
        chunker: An instance of `BaseChunker` to use when chunking long strings.
    """

    tokenizer: BaseTokenizer = field(kw_only=True)
    chunker: BaseChunker = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.chunker = TextChunker(tokenizer=self.tokenizer)

    def embed_text_artifact(self, artifact: TextArtifact) -> list[float]:
        return self.embed_string(artifact.to_text())

    def embed_string(self, string: str) -> list[float]:
        for attempt in self.retrying():
            with attempt:
                if self.tokenizer.count_tokens(string) > self.tokenizer.max_tokens:
                    return self._embed_long_string(string)
                else:
                    return self.try_embed_chunk(string)

        else:
            raise RuntimeError("Failed to embed string.")

    @abstractmethod
    def try_embed_chunk(self, chunk: str) -> list[float]:
        ...

    def _embed_long_string(self, string: str) -> list[float]:
        """Embeds a string that is too long to embed in one go.

        Adapted from: https://github.com/openai/openai-cookbook/blob/683e5f5a71bc7a1b0e5b7a35e087f53cc55fceea/examples/Embedding_long_inputs.ipynb
        """
        chunks = self.chunker.chunk(string)

        embedding_chunks = []
        length_chunks = []
        for chunk in chunks:
            embedding_chunks.append(self.try_embed_chunk(chunk.value))
            length_chunks.append(len(chunk))

        # generate weighted averages
        embedding_chunks = np.average(embedding_chunks, axis=0, weights=length_chunks)

        # normalize length to 1
        embedding_chunks = embedding_chunks / np.linalg.norm(embedding_chunks)

        return embedding_chunks.tolist()
