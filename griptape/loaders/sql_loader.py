from typing import Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers import BaseSqlDriver, BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class SqlLoader(BaseLoader):
    db_driver: BaseSqlDriver = field(kw_only=True)
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, select_query: str) -> list[TextArtifact]:
        return self._load_query(select_query)

    def load_collection(self, select_queries: dict[str, str]) -> dict[str, list[BaseArtifact]]:
        with self.futures_executor as executor:
            return utils.execute_futures_dict({
                key:
                    executor.submit(self._load_query, query)
                for key, query in select_queries.items()
            })

    def _load_query(self, query: str) -> list[TextArtifact]:
        rows = self.db_driver.execute_query(query)
        chunks = [TextArtifact(",".join([str(cell) for cell in row.cells])) for row in rows]
        artifacts = []

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts
