from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

from attrs import Attribute, Factory, define, field

from griptape.artifacts import BaseArtifact, BlobArtifact, ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.memory.meta import ActionSubtaskMetaEntry
from griptape.memory.task.storage import BlobArtifactStorage, TextArtifactStorage
from griptape.mixins.activity_mixin import ActivityMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.memory.task.storage import BaseArtifactStorage
    from griptape.tasks import ActionsSubtask


@define
class TaskMemory(ActivityMixin, SerializableMixin):
    name: str = field(
        default=Factory(lambda self: self.__class__.__name__, takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    artifact_storages: dict[type, BaseArtifactStorage] = field(
        default=Factory(
            lambda: {
                TextArtifact: TextArtifactStorage(),
                BlobArtifact: BlobArtifactStorage(),
            }
        ),
        kw_only=True,
    )
    namespace_storage: dict[str, BaseArtifactStorage] = field(
        factory=dict, kw_only=True, metadata={"serializable": True}
    )
    namespace_metadata: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})

    @artifact_storages.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_artifact_storages(self, _: Attribute, artifact_storage: dict[type, BaseArtifactStorage]) -> None:
        seen_types = []

        for storage in artifact_storage.values():
            if type(storage) in seen_types:
                raise ValueError("can't have more than memory storage of the same type")

            seen_types.append(type(storage))

    def get_storage_for(self, artifact: BaseArtifact) -> Optional[BaseArtifactStorage]:
        def find_storage(a: BaseArtifact) -> Optional[BaseArtifactStorage]:
            return next((v for k, v in self.artifact_storages.items() if isinstance(a, k)), None)

        if isinstance(artifact, ListArtifact):
            if artifact.has_items():
                return find_storage(artifact.value[0])
            return None
        return find_storage(artifact)

    def process_output(
        self,
        tool_activity: Callable,
        subtask: ActionsSubtask,
        output_artifact: BaseArtifact,
    ) -> BaseArtifact:
        from griptape.utils import J2

        tool_name = getattr(getattr(tool_activity, "__self__"), "name")
        activity_name = getattr(tool_activity, "name")
        namespace = output_artifact.name

        if output_artifact:
            result = self.store_artifact(namespace, output_artifact)

            if result:
                return result
            self.namespace_metadata[namespace] = subtask.actions_to_json()

            output = J2("memory/tool.j2").render(
                memory_name=self.name,
                tool_name=tool_name,
                activity_name=activity_name,
                artifact_namespace=namespace,
            )

            if subtask.structure and subtask.structure.meta_memory:
                subtask.structure.meta_memory.add_entry(
                    ActionSubtaskMetaEntry(
                        thought=subtask.thought,
                        actions=subtask.actions_to_json(),
                        answer=output,
                    ),
                )

            return InfoArtifact(output, name=namespace)
        return InfoArtifact("tool output is empty")

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> Optional[BaseArtifact]:
        namespace_storage = self.namespace_storage.get(namespace)
        storage = self.get_storage_for(artifact)

        if not storage:
            return artifact
        if namespace_storage and namespace_storage != storage:
            return ErrorArtifact("error storing tool output in memory")
        if storage:
            if isinstance(artifact, ListArtifact):
                for a in artifact.value:
                    storage.store_artifact(namespace, a)

                self.namespace_storage[namespace] = storage

                return None
            if isinstance(artifact, BaseArtifact):
                storage.store_artifact(namespace, artifact)

                self.namespace_storage[namespace] = storage

                return None
            return ErrorArtifact("error storing tool output in memory")
        return ErrorArtifact("error storing tool output in memory")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        storage = self.namespace_storage.get(namespace)

        if storage:
            return storage.load_artifacts(namespace)
        return ListArtifact()

    def find_input_memory(self, memory_name: str) -> Optional[TaskMemory]:
        if memory_name == self.name:
            return self
        return None
