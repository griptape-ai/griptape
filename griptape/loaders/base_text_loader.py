from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.chunkers import BaseChunker, TextChunker
from griptape.loaders import BaseLoader
from griptape.tokenizers import OpenAiTokenizer

if TYPE_CHECKING:
    from griptape.common import Reference
    from griptape.drivers import BaseEmbeddingDriver


@define
class BaseTextLoader(BaseLoader, ABC):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_input_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True,
    )
    chunker: BaseChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens),
            takes_self=True,
        ),
        kw_only=True,
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)
    reference: Optional[Reference] = field(default=None, kw_only=True)

    @abstractmethod
    def load(self, source: Any, *args, **kwargs) -> ErrorArtifact | list[TextArtifact]: ...

    def load_collection(self, sources: list[Any], *args, **kwargs) -> dict[str, ErrorArtifact | list[TextArtifact]]:
        return cast(
            dict[str, Union[ErrorArtifact, list[TextArtifact]]],
            super().load_collection(sources, *args, **kwargs),
        )

    def _text_to_artifacts(self, text: str) -> list[TextArtifact]:
        artifacts = []

        chunks = self.chunker.chunk(text) if self.chunker else [TextArtifact(text)]

        for chunk in chunks:
            if self.embedding_driver:
                chunk.generate_embedding(self.embedding_driver)

            chunk.reference = self.reference

            chunk.encoding = self.encoding

            artifacts.append(chunk)

        return artifacts
