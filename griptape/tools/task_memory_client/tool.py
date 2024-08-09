from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define
from schema import Literal, Schema

from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact, TextArtifact


@define
class TaskMemoryClient(BaseTool):
    @activity(
        config={
            "description": "Can be used to summarize memory content",
            "schema": Schema({"memory_name": str, "artifact_namespace": str}),
        },
    )
    def summarize(self, params: dict) -> TextArtifact | InfoArtifact | ErrorArtifact: ...

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
    def query(self, params: dict) -> BaseArtifact: ...
