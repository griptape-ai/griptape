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
        record_names = []

        if value:
            sources = value.get("records", {}).get("sources", [])

            for source in sources:
                if source["ramp_name"] == self.name:
                    record_names.extend(source["record_names"])

        if len(record_names) > 0:
            new_value = value.copy()

            new_value.update({"records": {"values": []}})

            for record_name in record_names:
                artifact = self.load_artifact(record_name)

                if artifact:
                    new_value["records"]["values"].append(artifact.to_dict())

            return new_value
        else:
            return value

    @abstractmethod
    def load_artifact(self, name: str) -> Optional[BaseArtifact]:
        ...
    