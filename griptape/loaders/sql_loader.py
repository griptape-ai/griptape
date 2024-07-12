from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from attrs import define, field

from griptape.artifacts import CsvRowArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver, BaseSqlDriver


@define
class SqlLoader(BaseLoader):
    sql_driver: BaseSqlDriver = field(kw_only=True)
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, source: str, *args, **kwargs) -> list[CsvRowArtifact]:
        rows = self.sql_driver.execute_query(source)
        artifacts = []

        chunks = [CsvRowArtifact(row.cells) for row in rows] if rows else []

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def load_collection(self, sources: list[str], *args, **kwargs) -> dict[str, list[CsvRowArtifact]]:
        return cast(dict[str, list[CsvRowArtifact]], super().load_collection(sources, *args, **kwargs))
