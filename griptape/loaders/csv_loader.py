from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING, Optional, Union, cast

from attrs import define, field

from griptape.artifacts import CsvRowArtifact, ErrorArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver


@define
class CsvLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    delimiter: str = field(default=",", kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: bytes | str, *args, **kwargs) -> ErrorArtifact | list[CsvRowArtifact]:
        artifacts = []

        if isinstance(source, bytes):
            try:
                source = source.decode(encoding=self.encoding)
            except UnicodeDecodeError:
                return ErrorArtifact(f"Failed to decode bytes to string using encoding: {self.encoding}")
        elif isinstance(source, (bytearray, memoryview)):
            return ErrorArtifact(f"Unsupported source type: {type(source)}")

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
    ) -> dict[str, ErrorArtifact | list[CsvRowArtifact]]:
        return cast(
            dict[str, Union[ErrorArtifact, list[CsvRowArtifact]]],
            super().load_collection(sources, *args, **kwargs),
        )
