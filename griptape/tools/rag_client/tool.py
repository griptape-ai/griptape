from __future__ import annotations
from attrs import define, field
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact, BaseArtifact
from griptape.engines.rag import RagEngine
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define(kw_only=True)
class RagClient(BaseTool):
    """
    Attributes:
        description: LLM-friendly RAG engine description.
        rag_engine: `RagEngine`.
    """

    description: str = field()
    rag_engine: RagEngine = field()

    @activity(
        config={
            "description": "{{ _self.description }}",
            "schema": Schema({Literal("query", description="A natural language search query"): str}),
        }
    )
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]

        try:
            result = self.rag_engine.process_query(query)

            if result.output is None:
                return ErrorArtifact("query output is empty")
            else:
                return result.output
        except Exception as e:
            return ErrorArtifact(f"error querying: {e}")
