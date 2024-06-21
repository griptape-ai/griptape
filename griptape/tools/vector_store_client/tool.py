from __future__ import annotations
from typing import Optional
from attrs import define, field
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact
from griptape.artifacts import ListArtifact
from griptape.drivers import BaseVectorStoreDriver
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class VectorStoreClient(BaseTool):
    """
    Attributes:
        description: LLM-friendly vector DB description.
        namespace: Vector storage namespace.
        vector_store_driver: `BaseVectorStoreDriver`.
        top_n: Max number of results returned for the query engine query.
    """

    DEFAULT_TOP_N = 5

    description: str = field(kw_only=True)
    vector_store_driver: BaseVectorStoreDriver = field(kw_only=True)
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
    def search(self, params: dict) -> ListArtifact | ErrorArtifact:
        query = params["values"]["query"]

        try:
            entries = self.vector_store_driver.query(query, namespace=self.namespace, count=self.top_n)

            return ListArtifact([e.to_artifact() for e in entries])
        except Exception as e:
            return ErrorArtifact(f"error querying vector store: {e}")
