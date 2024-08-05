from __future__ import annotations

from attrs import define
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class TaskMemoryClient(BaseTool):
    ARTIFACT_REFERENCE_SCHEMA = {
        "memory_name": str,
        "artifact_namespace": str,
    }

    @activity(
        config={
            "description": "Can be used to summarize memory content",
            "schema": Schema(ARTIFACT_REFERENCE_SCHEMA),
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
                    **ARTIFACT_REFERENCE_SCHEMA,
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

    @activity(
        config={
            "description": "Can be used extract memory content in JSON format",
            "schema": Schema(ARTIFACT_REFERENCE_SCHEMA),
        },
    )
    def extract_json(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]

        if memory:
            return memory.extract_json_namespace(artifact_namespace)
        else:
            return ErrorArtifact("memory not found")

    @activity(
        config={
            "description": "Can be used extract memory content in CSV format",
            "schema": Schema(ARTIFACT_REFERENCE_SCHEMA),
        },
    )
    def extract_csv(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]

        if memory:
            return memory.extract_csv_namespace(artifact_namespace)
        else:
            return ErrorArtifact("memory not found")
