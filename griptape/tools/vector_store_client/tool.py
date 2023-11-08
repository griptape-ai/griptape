from typing import Optional
from griptape.engines import VectorQueryEngine
from schema import Schema, Literal
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class VectorStoreClient(BaseTool):
    """
    Attributes:
        description: LLM-friendly vector DB description.
        namespace: Vector storage namespace.
        query_engine: `BaseQueryEngine`.
        top_n: Max number of results returned for the query engine query.
    """

    DEFAULT_TOP_N = 5

    description: str = field(kw_only=True)
    query_engine: VectorQueryEngine = field(kw_only=True)
    top_n: int = field(default=DEFAULT_TOP_N, kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    @activity(
        config={
            "description": "Can be used to search a vector database with the following description: {{ _self.description }}",
            "schema": Schema(
                {
                    Literal(
                        "query", description="A natural language search query to run against the vector database"
                    ): str
                }
            ),
        }
    )
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]

        try:
            return self.query_engine.query(query, top_n=self.top_n, namespace=self.namespace)
        except Exception as e:
            return ErrorArtifact(f"error querying vector store: {e}")
