from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import field, define
from schema import Schema, Literal
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.memory.tool import TextToolMemory


@define(slots=False)
class TextMemoryActivitiesMixin:
    max_search_results: int = field(default=5, kw_only=True)

    @activity(config={
        "description": "Can be used to insert text into a memory",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            "text": str
        })
    })
    def insert(self, params: dict) -> InfoArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        text = params["values"]["text"]

        if memory:
            memory.query_engine.upsert_text_artifact(TextArtifact(text), artifact_namespace)

            return InfoArtifact("text was successfully inserted")
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to extract and format content from memory into CSV output",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            Literal(
                "column_names",
                description="Column names for the CSV file"
            ): list[str]
        })
    })
    def extract_csv_rows(self, params: dict) -> ListArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        column_names = params["values"]["column_names"]

        if memory:
            return memory.csv_extraction_engine.extract(
                memory.load_artifacts(artifact_namespace),
                column_names
            )
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to extract and format content from memory into a list of JSON objects. Each object "
                       "is extracted based on the JSON schema.",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            Literal(
                "json_schema",
                description="JSON schema for an individual JSON object."
            ): dict
        })
    })
    def extract_json_objects(self, params: dict) -> ListArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        json_schema = params["values"]["json_schema"]

        if memory:
            return memory.json_extraction_engine.extract(
                memory.load_artifacts(artifact_namespace),
                json_schema
            )
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to summarize memory content",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str
        })
    })
    def summarize(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]

        if memory:
            return memory.summary_engine.summarize_artifacts(
                memory.load_artifacts(artifact_namespace),
            )
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to search and query memory content",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        if memory:
            return memory.query_engine.query(
                query,
                top_n=self.max_search_results,
                metadata=memory.namespace_metadata.get(artifact_namespace),
                namespace=artifact_namespace
            )
        else:
            return ErrorArtifact("memory not found")

    @abstractmethod
    def find_input_memory(self, memory_name: str) -> Optional[TextToolMemory]:
        ...
