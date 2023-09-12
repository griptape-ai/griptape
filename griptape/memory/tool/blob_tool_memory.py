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
            value: BaseArtifact
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name

        if isinstance(value, BlobArtifact):
            namespace = value.name

            self.driver.save(namespace, value)
        elif isinstance(value, ListArtifact) and value.is_type(BlobArtifact):
            artifacts = [v for v in value.value]

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

            return value

    def load_artifacts(self, namespace: str) -> list[BaseArtifact]:
        return self.driver.load(namespace)
