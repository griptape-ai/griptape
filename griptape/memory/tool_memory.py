from __future__ import annotations
import logging
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact, InfoArtifact, ListArtifact
from griptape.artifacts import BlobArtifact
from griptape.drivers import LocalBlobToolMemoryDriver
from griptape.engines import (
    BaseSummaryEngine, PromptSummaryEngine, BaseQueryEngine, CsvExtractionEngine, JsonExtractionEngine
)
from griptape.mixins import ActivityMixin
from griptape.mixins import ToolMemoryActivitiesMixin

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask
    from griptape.drivers import BaseBlobToolMemoryDriver


@define
class ToolMemory(ToolMemoryActivitiesMixin, ActivityMixin):
    class ProcessingState:
        UNPROCESSED = 1
        PROCESSED = 2
        EMPTY = 3

    name: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
    )
    namespace_metadata: dict[str, any] = field(factory=dict, kw_only=True)

    query_engine: BaseQueryEngine = field(
        kw_only=True
    )
    blob_storage_driver: BaseBlobToolMemoryDriver = field(
        default=Factory(lambda: LocalBlobToolMemoryDriver()),
        kw_only=True
    )
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )
    csv_extraction_engine: CsvExtractionEngine = field(
        kw_only=True,
        default=Factory(lambda: CsvExtractionEngine())
    )
    json_extraction_engine: JsonExtractionEngine = field(
        kw_only=True,
        default=Factory(lambda: JsonExtractionEngine())
    )

    def process_output(
            self,
            tool_activity: callable,
            subtask: ActionSubtask,
            output_artifact: BaseArtifact
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name
        namespace = output_artifact.name
        state = self.ProcessingState.UNPROCESSED

        if isinstance(output_artifact, TextArtifact):
            self.query_engine.upsert_text_artifact(
                output_artifact,
                namespace=namespace
            )

            self.namespace_metadata[namespace] = {
                "storage": self.query_engine
            }

            state = self.ProcessingState.PROCESSED
        elif isinstance(output_artifact, ListArtifact):
            if output_artifact.value:
                self.query_engine.upsert_text_artifact(
                    TextArtifact(output_artifact.to_text()),
                    namespace
                )

                self.namespace_metadata[namespace] = {
                    "storage": self.query_engine
                }

                state = self.ProcessingState.PROCESSED
            else:
                state = self.ProcessingState.EMPTY
        elif isinstance(output_artifact, BlobArtifact):
            self.blob_storage_driver.save(namespace, output_artifact)

            self.namespace_metadata[namespace] = {
                "storage": self.blob_storage_driver
            }

            state = self.ProcessingState.PROCESSED
        elif isinstance(output_artifact, ListArtifact) and output_artifact.is_type(BlobArtifact):
            if output_artifact.value:
                artifact_values = [v for v in output_artifact.value]

                [self.blob_storage_driver.save(namespace, a) for a in artifact_values]

                self.namespace_metadata[namespace] = {
                    "storage": self.blob_storage_driver
                }

                state = self.ProcessingState.PROCESSED
            else:
                state = self.ProcessingState.EMPTY

        if state is self.ProcessingState.PROCESSED:
            self.namespace_metadata[namespace] = subtask.action_to_json()

            output = J2("memory/tool.j2").render(
                memory_name=self.name,
                tool_name=tool_name,
                activity_name=activity_name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        elif state is self.ProcessingState.EMPTY:
            return InfoArtifact("Tool output is empty.")
        else:
            logging.info(f"Output of {tool_name}.{activity_name} can't be processed by memory {self.name}")

            return output_artifact

    def load_artifacts(self, namespace: str) -> ListArtifact:
        storage = self.namespace_metadata.get("namespace", {}).get("storage")

        if storage:
            if isinstance(storage, BaseQueryEngine):
                return storage.load_artifacts(namespace)
            elif isinstance(storage, BaseBlobToolMemoryDriver):
                return ListArtifact(storage.load(namespace))
            else:
                return ListArtifact()
        else:
            return ListArtifact()

    def find_input_memory(self, memory_name: str) -> Optional[ToolMemory]:
        if memory_name == self.name:
            return self
        else:
            return None
