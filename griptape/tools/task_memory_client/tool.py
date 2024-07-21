from __future__ import annotations

from attrs import define
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class TaskMemoryClient(BaseTool):
    @activity(
        config={
            "description": "Can be used to summarize memory content",
            "schema": Schema({"memory_name": str, "artifact_namespace": str}),
        },
    )
    def summarize(self, params: dict) -> TextArtifact | InfoArtifact | ErrorArtifact:
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
                },
            ),
        },
    )
    def query(self, params: dict) -> BaseArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        if memory:
            return memory.query_namespace(namespace=artifact_namespace, query=query)
        else:
            return ErrorArtifact("memory not found")
