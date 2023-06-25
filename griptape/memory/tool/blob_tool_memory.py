from __future__ import annotations
import logging
import uuid
from typing import Union, TYPE_CHECKING
from attr import define, field, Factory
from griptape.artifacts import BlobArtifact, BaseArtifact, InfoArtifact
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
            value: Union[BaseArtifact, list[BaseArtifact]]
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = tool_activity.__self__.name
        activity_name = tool_activity.name

        if isinstance(value, BlobArtifact):
            namespace = value.id

            self.driver.save(namespace, value)
        elif isinstance(value, list):
            artifacts = [a for a in value if isinstance(a, BlobArtifact)]

            if len(artifacts) > 0:
                namespace = uuid.uuid4().hex

                [self.driver.save(namespace, a) for a in artifacts]
            else:
                namespace = None
        else:
            namespace = None

        if namespace:
            self.namespace_metadata[namespace] = subtask.to_json()

            output = J2("memory/tool/blob.j2").render(
                memory_id=self.id,
                tool_name=tool_name,
                activity_name=activity_name,
                artifact_namespace=namespace
            )

            return InfoArtifact(output)
        else:
            logging.info(f"Output of {tool_name}.{activity_name} can't be processed by memory {self.id}")

            return value

    def load_artifacts(self, namespace: str) -> list[BaseArtifact]:
        return self.driver.load(namespace)
