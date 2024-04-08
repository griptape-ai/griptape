from __future__ import annotations
from io import BufferedIOBase, BytesIO, RawIOBase

from attr import define, field, Factory
from typing import IO, Optional, cast
from collections.abc import Sequence

from pathlib import Path

from griptape.loaders import BaseTextLoader
from griptape.utils import import_optional_dependency
from griptape.artifacts import TextArtifact
from griptape.chunkers import PdfChunker


@define
class PdfLoader(BaseTextLoader):
    chunker: PdfChunker = field(
        default=Factory(lambda self: PdfChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True),
        kw_only=True,
    )
    encoding: str = field(default=None, kw_only=True)

    def load(self, source: bytes | IO | Path, password: Optional[str] = None, *args, **kwargs) -> list[TextArtifact]:
        PdfReader = import_optional_dependency("pypdf").PdfReader
        with self._stream_from_source(source) as stream:
            reader = PdfReader(stream, strict=True, password=password)
            return self._text_to_artifacts("\n".join([p.extract_text() for p in reader.pages]))

    def _stream_from_source(self, source: bytes | IO | Path) -> IO:
        if isinstance(source, bytes):
            return BytesIO(source)
        elif isinstance(source, str):
            return open(source, "rb")
        elif isinstance(source, (RawIOBase, BufferedIOBase)):
            return cast(IO, source)
        elif isinstance(source, Path):
            return open(source, "rb")
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def load_collection(
        self, sources: Sequence[bytes | str | IO | Path], *args, **kwargs
    ) -> dict[str, list[TextArtifact]]:
        return cast(dict[str, list[TextArtifact]], super().load_collection(sources, *args, **kwargs))
