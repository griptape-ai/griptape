from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, InfoArtifact, ListArtifact
from griptape.mixins import ActivityMixin
from griptape.mixins import ToolMemoryActivitiesMixin

if TYPE_CHECKING:
    from griptape.memory.tool.storage import BaseToolMemoryStorage
    from griptape.tasks import ActionSubtask


@define
class ToolMemory(ToolMemoryActivitiesMixin, ActivityMixin):
    name: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
    )
    namespace_drivers: dict[str, BaseToolMemoryStorage] = field(factory=dict, kw_only=True)
    namespace_metadata: dict[str, any] = field(factory=dict, kw_only=True)

    memory_storage: list[BaseToolMemoryStorage] = field(kw_only=True)

    @memory_storage.validator
    def validate_memory_storage(self, _, memory_drivers: list[BaseToolMemoryStorage]) -> None:
        seen_types = []

        for driver in memory_drivers:
            if type(driver) in seen_types:
                raise ValueError("Can't have more than memory storage of the same type")

            seen_types.append(type(driver))

    def get_memory_driver_for(self, artifact: BaseArtifact) -> Optional[BaseToolMemoryStorage]:
        find_driver = lambda a: next(
            (driver for driver in self.memory_storage if driver.can_store(a)),
            None
        )

        if isinstance(artifact, ListArtifact):
            if artifact.has_items():
                return find_driver(artifact.value[0])
            else:
                return None
        else:
            return find_driver(artifact)

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

        if output_artifact.is_empty():
            return InfoArtifact("Tool output is empty.")
        elif self.store_artifact(namespace, output_artifact):
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

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> bool:
        driver = self.get_memory_driver_for(artifact)

        if driver:
            if isinstance(artifact, ListArtifact):
                [
                    driver.store_artifact(namespace, a)
                    for a in artifact.value
                ]

                self.namespace_drivers[namespace] = driver

                return True
            elif isinstance(artifact, BaseArtifact):
                driver.store_artifact(namespace, artifact)

                self.namespace_drivers[namespace] = driver

                return True
            else:
                return False
        else:
            return False

    def load_artifacts(self, namespace: str) -> ListArtifact:
        driver = self.namespace_drivers.get(namespace)

        if driver:
            return driver.load_artifacts(namespace)
        else:
            return ListArtifact()

    def find_input_memory(self, memory_name: str) -> Optional[ToolMemory]:
        if memory_name == self.name:
            return self
        else:
            return None
