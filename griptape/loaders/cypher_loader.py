from __future__ import annotations
from attr import define, field
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import CypherDriver
from griptape.loaders import BaseLoader

@define
class CypherLoader(BaseLoader):
    cypher_driver: CypherDriver = field(kw_only=True)

    def load(self, cypher_query: str) -> list[CsvRowArtifact]:
        rows = self.cypher_driver.execute_query(cypher_query)
        return [CsvRowArtifact(row.properties) for row in rows]

    def load_collection(self, cypher_queries: list[str]) -> dict[str, list[CsvRowArtifact]]:
        return {
            query: self.load(query) for query in cypher_queries
        }