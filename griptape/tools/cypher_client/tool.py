from __future__ import annotations
from attr import define, field
from griptape.artifacts import InfoArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.loaders import CypherLoader
from schema import Schema
from griptape.utils.decorators import activity

@define
class CypherClient(BaseTool):
    cypher_loader: CypherLoader = field(kw_only=True)

    @activity(config={
        "description":
            "Execute a Cypher query on the Neo4j database. "
            "You have to write the Cypher queries yourself. "
            "Never use '.name' in a query. ",
        "schema": Schema({
            "cypher_query": str
        })
    })
    def execute_query(self, params: dict) -> ListArtifact | InfoArtifact:
        query = params["values"]["cypher_query"]
        rows = self.cypher_loader.load(query)

        if rows:
            return ListArtifact(rows)
        else:
            return InfoArtifact("No results found")