from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define
from schema import Schema, Literal
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.memory import ToolMemory


@define(slots=False)
class ToolMemoryActivitiesMixin:
    @activity(
        config={
            "description": "Can be used to summarize memory content",
            "schema": Schema({"memory_name": str, "artifact_namespace": str}),
        }
    )
    def summarize(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]

        if memory:
            return memory.summarize_namespace(artifact_namespace)
        else:
            return ErrorArtifact("memory not found")

    @activity(
        config={
            "description": "Can be used to search and query memory content",
            "schema": Schema(
                {
                    "memory_name": str,
                    "artifact_namespace": str,
                    Literal(
                        "query",
                        description="A natural language search query in the form of a question with enough "
                        "contextual information for another person to understand what the query is about",
                    ): str,
                }
            ),
        }
    )
    def query(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        if memory:
            return memory.query_namespace(
                namespace=artifact_namespace, query=query
            )
        else:
            return ErrorArtifact("memory not found")

    @abstractmethod
    def find_input_memory(self, memory_name: str) -> Optional[ToolMemory]:
        ...
