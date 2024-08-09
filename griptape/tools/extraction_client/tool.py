from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Or, Schema

from griptape.artifacts import ErrorArtifact
from griptape.engines import CsvExtractionEngine, JsonExtractionEngine
from griptape.mixins import RuleMixin
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import InfoArtifact, ListArtifact
    from griptape.engines import BaseExtractionEngine


@define(kw_only=True)
class ExtractionClient(BaseTool, RuleMixin):
    """Tool for using an Extraction Engine.

    Attributes:
        extraction_engine: `ExtractionEngine`.
    """

    extraction_engine: BaseExtractionEngine = field()

    def __attrs_post_init__(self) -> None:
        if isinstance(self.extraction_engine, CsvExtractionEngine):
            self.allowlist = ["extract_csv"]
        elif isinstance(self.extraction_engine, JsonExtractionEngine):
            self.allowlist = ["extract_json"]

    @activity(
        config={
            "description": "Can be used extract data in JSON format",
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
    def extract_json(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        return self._extract(params)

    @activity(
        config={
            "description": "Can be used extract data in CSV format",
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
    def extract_csv(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        return self._extract(params)

    def _extract(self, params: dict) -> ListArtifact | InfoArtifact | ErrorArtifact:
        data = params["values"]["data"]

        if isinstance(data, str):
            return self.extraction_engine.extract(data, rulesets=self.rulesets)
        else:
            memory = self.find_input_memory(data["memory_name"])
            artifact_namespace = data["artifact_namespace"]

            if memory is not None:
                return self.extraction_engine.extract(memory.load_artifacts(artifact_namespace))
            else:
                return ErrorArtifact("memory not found")
