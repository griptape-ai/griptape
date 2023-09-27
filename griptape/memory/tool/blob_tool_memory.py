from __future__ import annotations
import logging
import uuid
from typing import TYPE_CHECKING
from attr import define, field, Factory
from griptape.artifacts import BlobArtifact, BaseArtifact, InfoArtifact, ListArtifact
from griptape.drivers import BaseBlobToolMemoryDriver, LocalBlobToolMemoryDriver
from griptape.memory.tool import BaseToolMemory

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class BlobToolMemory(BaseToolMemory):
    driver: BaseBlobToolMemoryDriver = field(
        default=Factory(lambda: LocalBlobToolMemoryDriver()),
        kw_only=True
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

        if isinstance(output_artifact, BlobArtifact):
            namespace = output_artifact.name

            self.driver.save(namespace, output_artifact)
        elif isinstance(output_artifact, ListArtifact) and output_artifact.is_type(BlobArtifact):
            artifacts = [v for v in output_artifact.value]

            if artifacts:
                namespace = uuid.uuid4().hex

                [self.driver.save(namespace, a) for a in artifacts]
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
        return ListArtifact(
            self.driver.load(namespace)
        )
