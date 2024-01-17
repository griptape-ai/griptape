from typing import Optional

from attr import define, field

from griptape import utils
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseSqlDriver, BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class SqlLoader(BaseLoader):
    sql_driver: BaseSqlDriver = field(kw_only=True)
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, source: str, *args, **kwargs) -> list[CsvRowArtifact]:
        return self._load_query(source)

    def load_collection(self, sources: list[str], *args, **kwargs) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {utils.str_to_hash(source): self.futures_executor.submit(self._load_query, source) for source in sources}
        )

    def _load_query(self, query: str) -> list[CsvRowArtifact]:
        rows = self.sql_driver.execute_query(query)
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
