import os
from typing import Optional, Union
import numpy as np
import openai
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class OpenAiEmbeddingDriver(BaseEmbeddingDriver):
    DEFAULT_MODEL = "text-embedding-ada-002"
    DEFAULT_DIMENSIONS = 1536

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    dimensions: int = field(default=DEFAULT_DIMENSIONS, kw_only=True)
    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )

    def __attrs_post_init__(self) -> None:
        openai.api_type = self.api_type
        openai.api_version = self.api_version
        openai.api_base = self.api_base
        openai.api_key = self.api_key
        openai.organization = self.organization

    def try_embed_string(self, string: str) -> list[float]:
        # Address a performance issue in older ada models
        # https://github.com/openai/openai-python/issues/418#issuecomment-1525939500
        if self.model.endswith("001"):
            string = string.replace("\n", " ")

        if self.tokenizer.token_count(string) > self.tokenizer.max_tokens:
            return self.embed_long_string(string)
        else:
            return self.embed_chunk(string)

    def embed_chunk(self, chunk: Union[list[int], str]) -> list[float]:
        return openai.Embedding.create(
            input=chunk,
            model=self.model
        )["data"][0]["embedding"]

    def embed_long_string(self, string: str) -> list[float]:
        tokens = self.tokenizer.encode(string)
        chunked_tokens = self.tokenizer.chunk_tokens(tokens)
        embedding_chunks = []
        length_chunks = []

        for chunk in chunked_tokens:
            embedding_chunks.append(self.embed_chunk(chunk))
            length_chunks.append(len(chunk))

        # generate weighted averages
        embedding_chunks = np.average(embedding_chunks, axis=0, weights=length_chunks)

        # normalize length to 1
        embedding_chunks = embedding_chunks / np.linalg.norm(embedding_chunks)

        return embedding_chunks.tolist()
