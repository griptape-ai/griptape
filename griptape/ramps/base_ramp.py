from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact
from griptape.core import ActivityMixin


@define
class BaseRamp(ActivityMixin, ABC):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        return self.load_artifacts(value)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        return artifact

    def load_artifacts(self, value: Optional[dict]) -> Optional[dict]:
        artifact_names = []

        if value:
            sources = value.get("artifacts", {}).get("sources", [])

            for source in sources:
                if source["ramp_name"] == self.name:
                    artifact_names.extend(source["artifact_names"])

        if len(artifact_names) > 0:
            new_value = value.copy()

            if not new_value.get("artifacts", {}).get("values"):
                new_value.update({"artifacts": {"values": []}})

            for artifact_name in artifact_names:
                artifact = self.load_artifact(artifact_name)

                if artifact:
                    new_value["artifacts"]["values"].append(artifact.to_dict())

            return new_value
        else:
            return value

    @abstractmethod
    def load_artifact(self, name: str) -> Optional[BaseArtifact]:
        ...
    