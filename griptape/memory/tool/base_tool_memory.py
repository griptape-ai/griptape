from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact
from griptape.core import ActivityMixin


@define
class BaseToolMemory(ActivityMixin, ABC):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        return self.load_artifacts(value)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        return artifact

    def load_artifacts(self, value: Optional[dict]) -> Optional[dict]:
        artifact_ids = []

        if value:
            sources = value.get("artifacts", {}).get("sources", [])

            for source in sources:
                if source["memory_name"] == self.name:
                    artifact_ids.extend(source["artifact_ids"])

        if len(artifact_ids) > 0:
            new_value = value.copy()

            if not new_value.get("artifacts", {}).get("values"):
                new_value.update({"artifacts": {"values": []}})

            for artifact_id in artifact_ids:
                [
                    new_value["artifacts"]["values"].append(a.to_dict())
                    for a in self.load_namespace_artifacts(artifact_id)
                ]

            return new_value
        else:
            return value

    @abstractmethod
    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...
    