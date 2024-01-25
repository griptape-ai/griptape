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

    def load(self, select_query: str) -> list[CsvRowArtifact]:
        return self._load_query(select_query)

    def load_collection(self, select_queries: list[str]) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {
                utils.str_to_hash(query): self.futures_executor.submit(self._load_query, query)
                for query in select_queries
            }
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
