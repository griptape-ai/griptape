from __future__ import annotations
import csv
from io import IOBase, StringIO
from pathlib import Path
from typing import IO, Any, Optional, cast
from collections.abc import Sequence

from attr import define, field

from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class CsvLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    delimiter: str = field(default=",", kw_only=True)

    def load(self, source: bytes | str | IO | Path, *args, **kwargs) -> list[CsvRowArtifact]:
        artifacts = []

        with self._stream_from_source(source) as stream:
            reader = csv.DictReader(stream, delimiter=self.delimiter)
            chunks = [CsvRowArtifact(row) for row in reader]

            if self.embedding_driver:
                for chunk in chunks:
                    chunk.generate_embedding(self.embedding_driver)

            for chunk in chunks:
                artifacts.append(chunk)

        return artifacts

    def _stream_from_source(self, source: bytes | str | IO | Path) -> IO:
        if isinstance(source, bytes):
            return StringIO(source.decode())
        elif isinstance(source, str):
            return StringIO(source)
        elif isinstance(source, IOBase):
            return cast(IO, source)
        elif isinstance(source, Path):
            return open(source, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def load_collection(
        self, sources: Sequence[bytes | str | IO | Path], *args, **kwargs
    ) -> dict[str, list[CsvRowArtifact]]:
        return cast(Any, super().load_collection(sources, *args, **kwargs))
