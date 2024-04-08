from __future__ import annotations

from io import StringIO, TextIOBase
from typing import IO, Optional, cast
from collections.abc import Sequence

from attr import field, define, Factory
from pathlib import Path

from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseTextLoader
from griptape.tokenizers import OpenAiTokenizer


@define
class TextLoader(BaseTextLoader):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)), kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_input_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True,
    )
    chunker: TextChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True
        ),
        kw_only=True,
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: bytes | str | IO | Path, *args, **kwargs) -> list[TextArtifact]:
        with self._stream_from_source(source) as stream:
            return self._text_to_artifacts(stream.read())

    def load_collection(
        self, sources: Sequence[bytes | str | IO | Path], *args, **kwargs
    ) -> dict[str, list[TextArtifact]]:
        return cast(dict[str, list[TextArtifact]], super().load_collection(sources, *args, **kwargs))

    def _stream_from_source(self, source: bytes | str | IO | Path) -> IO:
        if isinstance(source, bytes):
            return StringIO(source.decode())
        elif isinstance(source, str):
            return StringIO(source)
        elif issubclass(type(source), TextIOBase):
            return cast(IO, source)
        elif isinstance(source, Path):
            return open(source, encoding=self.encoding)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")
