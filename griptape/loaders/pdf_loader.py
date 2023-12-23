from __future__ import annotations
from pathlib import Path
from typing import IO, Optional
from PyPDF2 import PdfReader
from attr import define, field, Factory
from griptape.utils import str_to_hash, execute_futures_dict
from griptape.artifacts import TextArtifact
from griptape.chunkers import PdfChunker
from griptape.loaders import TextLoader


@define
class PdfLoader(TextLoader):
    chunker: PdfChunker = field(
        default=Factory(lambda self: PdfChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True),
        kw_only=True,
    )

    def load(self, stream: str | IO | Path, password: str | None = None) -> list[TextArtifact]:
        return self._load_pdf(stream, password)

    def load_collection(
        self, streams: list[str | IO | Path], password: str | None = None
    ) -> dict[str, list[TextArtifact]]:
        return execute_futures_dict(
            {
                str_to_hash(s.decode())
                if isinstance(s, bytes)
                else str_to_hash(str(s)): self.futures_executor.submit(self._load_pdf, s, password)
                for s in streams
            }
        )

    def _load_pdf(self, stream: str | IO | Path, password: str | None) -> list[TextArtifact]:
        reader = PdfReader(stream, strict=True, password=password)

        return self.text_to_artifacts("\n".join([p.extract_text() for p in reader.pages]))
