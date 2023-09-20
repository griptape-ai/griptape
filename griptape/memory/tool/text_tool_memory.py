from __future__ import annotations
import logging
import uuid
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact, ListArtifact
from griptape.engines import BaseSummaryEngine, PromptSummaryEngine, BaseQueryEngine, CsvExtractionEngine
from griptape.memory.tool import BaseToolMemory
from griptape.mixins import TextMemoryActivitiesMixin

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class TextToolMemory(BaseToolMemory, TextMemoryActivitiesMixin):
    query_engine: BaseQueryEngine = field(kw_only=True)
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )
    csv_extraction_engine: CsvExtractionEngine = field(
        kw_only=True,
        default=Factory(lambda: CsvExtractionEngine())
    )

    def process_output(
            self,
            tool_activity: callable,
            subtask: ActionSubtask,
            value: BaseArtifact
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name

        if isinstance(value, TextArtifact):
            namespace = value.name

            self.query_engine.upsert_text_artifact(
                value,
                namespace=namespace
            )
        elif isinstance(value, ListArtifact) and value.is_type(TextArtifact):
            artifacts = [v for v in value.value]

            if artifacts:
                namespace = uuid.uuid4().hex

                self.query_engine.upsert_text_artifacts(artifacts, namespace)
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

            return value

    def load_artifacts(self, namespace: str) -> list[TextArtifact]:
        artifacts = [
            BaseArtifact.from_json(e.meta["artifact"])
            for e in self.query_engine.vector_store_driver.load_entries(namespace)
        ]

        return [a for a in artifacts if isinstance(a, TextArtifact)]

    def find_input_memory(self, memory_name: str) -> Optional[TextToolMemory]:
        if memory_name == self.name:
            return self
        else:
            return None