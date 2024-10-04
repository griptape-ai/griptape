from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Or, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import InfoArtifact
    from griptape.engines import BaseExtractionEngine


@define(kw_only=True)
class ExtractionTool(BaseTool, RuleMixin):
    """Tool for using an Extraction Engine.

    Attributes:
        extraction_engine: `ExtractionEngine`.
    """

    extraction_engine: BaseExtractionEngine = field()

    @activity(
        config={
            "description": "Can be used extract structured text from data.",
            "schema": Schema(
                {
                    Literal("data"): Or(
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
    def extract(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        data = params["values"]["data"]

        if isinstance(data, str):
            artifacts = ListArtifact([TextArtifact(data)])
        else:
            memory = self.find_input_memory(data["memory_name"])
            artifact_namespace = data["artifact_namespace"]

            if memory is not None:
                artifacts = memory.load_artifacts(artifact_namespace)
            else:
                return ErrorArtifact("memory not found")

        return self.extraction_engine.extract_artifacts(artifacts)
