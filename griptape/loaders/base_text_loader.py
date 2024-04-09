from __future__ import annotations

from abc import ABC
from typing import Any, Optional, Union, cast

from attrs import define, field, Factory

from griptape.artifacts import TextArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.chunkers import TextChunker, BaseChunker
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader
from griptape.tokenizers import OpenAiTokenizer


@define
class BaseTextLoader(BaseLoader, ABC):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)), kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_input_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True,
    )
    chunker: BaseChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True
        ),
        kw_only=True,
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load_collection(self, sources: list[Any], *args, **kwargs) -> dict[str, ErrorArtifact | list[TextArtifact]]:
        return cast(
            dict[str, Union[ErrorArtifact, list[TextArtifact]]], super().load_collection(sources, *args, **kwargs)
        )

    def _text_to_artifacts(self, text: str) -> list[TextArtifact]:
        artifacts = []

        if self.chunker:
            chunks = self.chunker.chunk(text)
        else:
            chunks = [TextArtifact(text)]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            chunk.encoding = self.encoding
            artifacts.append(chunk)

        return artifacts
