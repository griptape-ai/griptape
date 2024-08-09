from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Or, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.engines import PromptSummaryEngine


@define(kw_only=True)
class PromptSummaryClient(BaseTool):
    """Tool for using a Prompt Summary Engine.

    Attributes:
        prompt_summary_engine: `PromptSummaryEngine`.
    """

    prompt_summary_engine: PromptSummaryEngine = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to summarize text content.",
            "schema": Schema(
                {
                    Literal("summary"): Or(
                        str,
                        Schema(
                            {
                                "memory_name": str,
                                "artifact_namespace": str,
                            }
                        ),
                    ),
                }
            ),
        },
    )
    def summarize(self, params: dict) -> BaseArtifact:
        summary = params["values"]["summary"]

        if isinstance(summary, str):
            artifacts = ListArtifact([TextArtifact(summary)])
        else:
            memory = self.find_input_memory(summary["memory_name"])
            artifact_namespace = summary["artifact_namespace"]

            if memory is not None:
                artifacts = memory.load_artifacts(artifact_namespace)
            else:
                return ErrorArtifact("memory not found")

        return self.prompt_summary_engine.summarize_artifacts(artifacts)
