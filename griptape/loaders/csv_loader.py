from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING, Optional, cast

from attrs import define, field

from griptape.artifacts import CsvRowArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver


@define
class CsvLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    delimiter: str = field(default=",", kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: bytes | str, *args, **kwargs) -> list[CsvRowArtifact]:
        artifacts = []

        if isinstance(source, bytes):
            source = source.decode(encoding=self.encoding)
        elif isinstance(source, (bytearray, memoryview)):
            raise ValueError(f"Unsupported source type: {type(source)}")

        reader = csv.DictReader(StringIO(source), delimiter=self.delimiter)
        chunks = [CsvRowArtifact(row) for row in reader]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def load_collection(
        self,
        sources: list[bytes | str],
        *args,
        **kwargs,
    ) -> dict[str, list[CsvRowArtifact]]:
        return cast(
            dict[str, list[CsvRowArtifact]],
            super().load_collection(sources, *args, **kwargs),
        )
