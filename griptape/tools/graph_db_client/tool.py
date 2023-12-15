from typing import Optional
from griptape.engines import GraphQueryEngine
from schema import Schema, Literal
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class GraphDbClient(BaseTool):
    description: str = field(kw_only=True)
    query_engine: GraphQueryEngine = field(kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    @activity(
        config={
            "description": "Can be used to search a graph database with the following description: {{ _self.description }}",
            "schema": Schema(
                {
                    Literal(
                        "query", description="A natural language search query to run against the graph database"
                    ): str
                }
            ),
        }
    )
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]

        try:
            return self.query_engine.query(query, namespace=self.namespace)
        except Exception as e:
            return ErrorArtifact(f"error querying graph database: {e}")
