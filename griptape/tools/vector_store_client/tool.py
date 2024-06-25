from __future__ import annotations
from typing import Callable, Any
from attrs import define, field, Factory
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact, BaseArtifact
from griptape.artifacts import ListArtifact
from griptape.drivers import BaseVectorStoreDriver
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define(kw_only=True)
class VectorStoreClient(BaseTool):
    """
    Attributes:
        description: LLM-friendly vector DB description.
        vector_store_driver: `BaseVectorStoreDriver`.
        query_params: Optional dictionary of vector store driver query parameters.
        process_query_output_fn: Optional lambda for processing vector store driver query output `Entry`s.
    """

    DEFAULT_TOP_N = 5

    description: str = field()
    vector_store_driver: BaseVectorStoreDriver = field()
    query_params: dict[str, Any] = field(factory=dict)
    process_query_output_fn: Callable[[list[BaseVectorStoreDriver.Entry]], BaseArtifact] = field(
        default=Factory(lambda: lambda es: ListArtifact([e.to_artifact() for e in es]))
    )

    @activity(
        config={
            "description": "Can be used to search a database with the following description: {{ _self.description }}",
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
            return self.process_query_output_fn(self.vector_store_driver.query(query, **self.query_params))
        except Exception as e:
            return ErrorArtifact(f"error querying vector store: {e}")
