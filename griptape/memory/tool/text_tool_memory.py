from __future__ import annotations
import logging
import uuid
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact, ListArtifact
from griptape.engines import (
    BaseSummaryEngine, BaseQueryEngine, CsvExtractionEngine, JsonExtractionEngine
)
from griptape.memory.tool import BaseToolMemory
from griptape.mixins import TextMemoryActivitiesMixin

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class TextToolMemory(BaseToolMemory, TextMemoryActivitiesMixin):
    query_engine: BaseQueryEngine = field(kw_only=True)
    summary_engine: BaseSummaryEngine = field(kw_only=True)
    csv_extraction_engine: CsvExtractionEngine = field(kw_only=True)
    json_extraction_engine: JsonExtractionEngine = field(kw_only=True)

    def process_output(
            self,
            tool_activity: callable,
            subtask: ActionSubtask,
            output_artifact: BaseArtifact
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name

        if isinstance(output_artifact, TextArtifact):
            namespace = output_artifact.name

            self.query_engine.upsert_text_artifact(
                output_artifact,
                namespace=namespace
            )
        elif isinstance(output_artifact, ListArtifact):
            if output_artifact.has_items():
                namespace = uuid.uuid4().hex

                self.query_engine.upsert_text_artifact(
                    TextArtifact(output_artifact.to_text()),
                    namespace
                )
            else:
                namespace = None
        else:
            namespace = None

        if namespace:
            self.namespace_metadata[namespace] = subtask.action_to_json()

            output = J2("memory/tool.j2").render(
                memory_name=self.name,
                tool_name=tool_name,
                activity_name=activity_name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        else:
            logging.info(f"Output of {tool_name}.{activity_name} can't be processed by memory {self.name}")

            return output_artifact

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return self.query_engine.load_artifacts(namespace)

    def find_input_memory(self, memory_name: str) -> Optional[TextToolMemory]:
        if memory_name == self.name:
            return self
        else:
            return None
