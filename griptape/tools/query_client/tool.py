from __future__ import annotations

from attrs import Factory, define, field
from schema import Literal, Or, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.config import config
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
)
from griptape.engines.rag.rag_context import RagContext
from griptape.engines.rag.stages import ResponseRagStage
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tools.rag_client.tool import RagClient
from griptape.utils.decorators import activity


@define(kw_only=True)
class QueryClient(RagClient, RuleMixin):
    """Tool for performing a query against data."""

    description: str = field(init=False)
    rag_engine: RagEngine = field(
        default=Factory(
            lambda self: RagEngine(
                response_stage=ResponseRagStage(
                    response_modules=[
                        PromptResponseRagModule(prompt_driver=config.drivers.prompt, rulesets=self.rulesets)
                    ],
                ),
            ),
            takes_self=True,
        ),
    )

    @activity(
        config={
            "description": "Can be used to search through textual content.",
            "schema": Schema(
                {
                    Literal("query", description="A natural language search query"): str,
                    Literal("content"): Or(
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
    def query(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]
        summary = params["values"]["content"]

        if isinstance(summary, str):
            text_artifacts = [TextArtifact(summary)]
        else:
            memory = self.find_input_memory(summary["memory_name"])
            artifact_namespace = summary["artifact_namespace"]

            if memory is not None:
                artifacts = memory.load_artifacts(artifact_namespace)
            else:
                return ErrorArtifact("memory not found")

            text_artifacts = [artifact for artifact in artifacts if isinstance(artifact, TextArtifact)]

        outputs = self.rag_engine.process(RagContext(query=query, text_chunks=text_artifacts)).outputs

        if len(outputs) > 0:
            return ListArtifact(outputs)
        else:
            return ErrorArtifact("query output is empty")
