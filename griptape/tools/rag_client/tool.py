from __future__ import annotations

from attrs import Factory, define, field
from schema import Literal, Or, Schema

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    MetadataBeforeResponseRagModule,
    PromptResponseRagModule,
    RulesetsBeforeResponseRagModule,
)
from griptape.engines.rag.rag_context import RagContext
from griptape.engines.rag.stages import ResponseRagStage
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define(kw_only=True)
class RagClient(BaseTool, RuleMixin):
    """Tool for querying a RAG engine.

    Attributes:
        description: LLM-friendly RAG engine description.
        rag_engine: `RagEngine`.
    """

    description: str = field()
    rag_engine: RagEngine = field(
        default=Factory(
            lambda self: RagEngine(
                response_stage=ResponseRagStage(
                    before_response_modules=[
                        RulesetsBeforeResponseRagModule(rulesets=self.all_rulesets),
                        MetadataBeforeResponseRagModule(),
                    ],
                    response_module=PromptResponseRagModule(),
                ),
            ),
            takes_self=True,
        )
    )

    @activity(
        config={
            "description": "Can be used to search content with the following description:  {{ _self.description }}",
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
    def search(self, params: dict) -> BaseArtifact:
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

        try:
            result = self.rag_engine.process(RagContext(query=query, text_chunks=text_artifacts))

            if result.output is None:
                return ErrorArtifact("query output is empty")
            else:
                return result.output
        except Exception as e:
            return ErrorArtifact(f"error querying: {e}")
