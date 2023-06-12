from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact


@define
class BaseToolMemory(ABC):
    id: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        return self.load_artifacts(value)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        return artifact

    def load_artifacts(self, value: Optional[dict]) -> Optional[dict]:
        if value:
            source = value.get("artifact", {}).get("source", {})

            if source.get("memory_id") == self.id:
                namespace = source["artifact_namespace"]
                new_value = value.copy()

                if not new_value.get("artifacts", {}).get("values"):
                    new_value.update({"artifacts": {"values": []}})

                for a in self.load_namespace_artifacts(namespace):
                    new_value["artifacts"]["values"].append(a)

                return new_value
            else:
                return value
        else:
            return value

    @abstractmethod
    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...
    