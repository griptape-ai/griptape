from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.engines.rag import RagEngine


@define(kw_only=True)
class RagTool(BaseTool):
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
    def search(self, params: dict) -> ListArtifact | ErrorArtifact:
        query = params["values"]["query"]

        try:
            artifacts = self.rag_engine.process_query(query).outputs

            outputs = []
            for artifact in artifacts:
                if isinstance(artifact, ListArtifact):
                    outputs.extend(artifact.value)
                else:
                    outputs.append(artifact)

            if len(outputs) > 0:
                return ListArtifact(outputs)
            else:
                return ErrorArtifact("query output is empty")

        except Exception as e:
            return ErrorArtifact(f"error querying: {e}")
