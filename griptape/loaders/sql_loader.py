from typing import Optional, cast

from attr import define, field

from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseSqlDriver, BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class SqlLoader(BaseLoader):
    sql_driver: BaseSqlDriver = field(kw_only=True)
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, source: str, *args, **kwargs) -> list[CsvRowArtifact]:
        rows = self.sql_driver.execute_query(source)
        artifacts = []

        if rows:
            chunks = [CsvRowArtifact(row.cells) for row in rows]
        else:
            chunks = []

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def load_collection(self, sources: list[str], *args, **kwargs) -> dict[str, list[CsvRowArtifact]]:
        return cast(dict[str, list[CsvRowArtifact]], super().load_collection(sources, *args, **kwargs))
