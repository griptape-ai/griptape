from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Any
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, InfoArtifact, ListArtifact, ErrorArtifact, TextArtifact
from griptape.memory.meta import ActionSubtaskMetaEntry
from griptape.mixins import ActivityMixin

if TYPE_CHECKING:
    from griptape.memory.task.storage import BaseArtifactStorage
    from griptape.tasks import ActionSubtask


@define
class TaskMemory(ActivityMixin):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    artifact_storages: dict[Type, BaseArtifactStorage] = field(factory=dict, kw_only=True)
    namespace_storage: dict[str, BaseArtifactStorage] = field(factory=dict, kw_only=True)
    namespace_metadata: dict[str, Any] = field(factory=dict, kw_only=True)

    @artifact_storages.validator
    def validate_artifact_storages(self, _, artifact_storage: dict[Type, BaseArtifactStorage]) -> None:
        seen_types = []

        for storage in artifact_storage.values():
            if type(storage) in seen_types:
                raise ValueError("can't have more than memory storage of the same type")

            seen_types.append(type(storage))

    def get_storage_for(self, artifact: BaseArtifact) -> Optional[BaseArtifactStorage]:
        find_storage = lambda a: next((v for k, v in self.artifact_storages.items() if isinstance(a, k)), None)

        if isinstance(artifact, ListArtifact):
            if artifact.has_items():
                return find_storage(artifact.value[0])
            else:
                return None
        else:
            return find_storage(artifact)

    def process_output(self, task: BaseTask, output_artifact: BaseArtifact) -> BaseArtifact:
        from griptape.tasks import ActionSubtask
        from griptape.utils import J2

        namespace = output_artifact.name

        if output_artifact:
            result = self.store_artifact(namespace, output_artifact)

            if result:
                return result
            else:
                namespace = output_artifact.name
                task_output_name = task.name
                if isinstance(task, ActionSubtask):
                    task_output_name = f"{task.action_name}.{task.action_path}"
                output = J2("memory/task.j2").render(
                    memory_name=self.name, task_output_name=task_output_name, artifact_namespace=namespace
                )

                if isinstance(task, ActionSubtask):
                    self.namespace_metadata[namespace] = task.action_to_json()
                    if task.structure and task.structure.meta_memory:
                        task.structure.meta_memory.add_entry(
                            ActionSubtaskMetaEntry(thought=task.thought, action=task.action_to_json(), answer=output)
                        )

                return InfoArtifact(output)
        else:
            return InfoArtifact("task output is empty")

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> Optional[BaseArtifact]:
        namespace_storage = self.namespace_storage.get(namespace)
        storage = self.get_storage_for(artifact)

        if not storage:
            return artifact
        elif namespace_storage and namespace_storage != storage:
            return ErrorArtifact("error storing tool output in memory")
        else:
            if storage:
                if isinstance(artifact, ListArtifact):
                    for a in artifact.value:
                        storage.store_artifact(namespace, a)

                    self.namespace_storage[namespace] = storage

                    return None
                elif isinstance(artifact, BaseArtifact):
                    storage.store_artifact(namespace, artifact)

                    self.namespace_storage[namespace] = storage

                    return None
                else:
                    return ErrorArtifact("error storing tool output in memory")
            else:
                return ErrorArtifact("error storing tool output in memory")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        storage = self.namespace_storage.get(namespace)

        if storage:
            return storage.load_artifacts(namespace)
        else:
            return ListArtifact()

    def find_input_memory(self, memory_name: str) -> Optional[TaskMemory]:
        if memory_name == self.name:
            return self
        else:
            return None

    def summarize_namespace(self, namespace: str) -> TextArtifact | InfoArtifact:
        storage = self.namespace_storage.get(namespace)

        if storage:
            return storage.summarize(namespace)
        else:
            return InfoArtifact("Can't find memory content")

    def query_namespace(self, namespace: str, query: str) -> TextArtifact | InfoArtifact:
        storage = self.namespace_storage.get(namespace)

        if storage:
            return storage.query(namespace=namespace, query=query, metadata=self.namespace_metadata.get(namespace))
        else:
            return InfoArtifact("Can't find memory content")
