from typing import Optional, Union
from attr import define, field
from schema import Schema, Literal

from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.core.decorators import activity
from griptape.drivers import MemoryTextStorageDriver, BaseTextStorageDriver
from griptape.ramps import BaseRamp


@define
class TextStorageRamp(BaseRamp):
    driver: BaseTextStorageDriver = field(default=MemoryTextStorageDriver(), kw_only=True)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> Union[InfoArtifact, ErrorArtifact]:
        from griptape.utils import J2

        if isinstance(artifact, TextArtifact):
            artifact_names = [self.driver.save(artifact.to_text())]
        elif isinstance(artifact, ListArtifact):
            artifact_names = [self.driver.save(a.to_text()) for a in artifact.value if isinstance(a, TextArtifact)]
        else:
            artifact_names = []

        if len(artifact_names) > 0:
            output = J2("ramps/text_storage.j2").render(
                ramp_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.name,
                names=str.join(", ", artifact_names)
            )

            return InfoArtifact(output)
        else:
            return artifact

    def load_artifact(self, name: str) -> Union[TextArtifact, ErrorArtifact]:
        value = self.driver.load(name)

        if value:
            return TextArtifact(value)
        else:
            return ErrorArtifact(f"can't find artifact {name}")

    @activity(config={
        "name": "save_value",
        "description": "Can be used to save artifact values",
        "schema": Schema({
            "artifact_value": str
        }),
    })
    def save_value(self, params: dict) -> Union[InfoArtifact, ErrorArtifact]:
        value = params["values"]["artifact_value"]
        name = self.driver.save(value)

        return InfoArtifact(f"Value was successfully stored with the following name: {name}")

    @activity(config={
        "name": "get_value",
        "description": "Can be used to load artifact values",
        "schema": Schema({
            "artifact_name": str
        })
    })
    def load_value(self, params: dict) -> Union[InfoArtifact, ErrorArtifact]:
        name = params["values"]["artifact_name"]
        value = self.driver.load(name)

        if value:
            return InfoArtifact(value)
        else:
            return ErrorArtifact(f"can't find artifact {name}")
