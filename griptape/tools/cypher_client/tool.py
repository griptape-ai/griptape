from __future__ import annotations
from typing import Optional
from attr import define, field
from griptape.artifacts import InfoArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.loaders import CypherLoader
from schema import Schema


@define
class CypherClient(BaseTool):
    cypher_loader: CypherLoader = field(kw_only=True)
    graph_name: Optional[str] = field(default=None, kw_only=True)
    engine_name: Optional[str] = field(default=None, kw_only=True)

    @property
    def full_graph_name(self) -> str:
        return self.graph_name

    @property
    def graph_schema(self) -> str:
        return self.cypher_loader.cypher_driver.get_schema()

    @activity(config={
        "description":
            "Can be used to execute a Cypher query on the Neo4j database {{ _self.full_graph_name }}. "
            "You have to write the Cypher queries yourself. "
            "Avoid using escape characters in your queries. Instead, enclose names that contain apostrophes in double quotes."
            "Be creative when you use `WHERE` statements: you can use wildcards, functions, and other Cypher constructs "
            "to get better results. "
            "You can use relationships and nodes available in the graph."
            "Graph schema: {{ _self.graph_schema }}"
            "{% if _self.engine_name %}Engine: {{ _self.engine_name }}{% endif %}",
        "schema": Schema({
            "cypher_query": str
        })
    })
    def execute_query(self, params: dict) -> ListArtifact | InfoArtifact:
        query = params["values"]["cypher_query"]
        rows = self.cypher_loader.load(query)

        if len(rows) > 0:
            return ListArtifact(rows)
        else:
            return InfoArtifact("No results found")
