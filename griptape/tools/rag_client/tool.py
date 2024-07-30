from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.engines.rag import RagEngine


@define(kw_only=True)
class RagClient(BaseTool):
    """Tool for querying a RAG engine.

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
        },
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
