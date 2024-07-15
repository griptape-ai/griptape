from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define(kw_only=True)
class VectorStoreClient(BaseTool):
    """A tool for querying a vector database.

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
        default=Factory(lambda: lambda es: ListArtifact([e.to_artifact() for e in es])),
    )

    @activity(
        config={
            "description": "Can be used to search a database with the following description: {{ _self.description }}",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="A natural language search query to run against the vector database",
                    ): str,
                },
            ),
        },
    )
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]

        try:
            return self.process_query_output_fn(self.vector_store_driver.query(query, **self.query_params))
        except Exception as e:
            return ErrorArtifact(f"error querying vector store: {e}")
