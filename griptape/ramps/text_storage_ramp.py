from typing import Union, Optional
from attr import define, field
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.ramps import BaseRamp
from griptape.drivers import MemoryTextStorageDriver, BaseTextStorageDriver


@define
class TextStorageRamp(BaseRamp):
    driver: BaseTextStorageDriver = field(default=MemoryTextStorageDriver(), kw_only=True)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(artifact, TextArtifact):
            key = self.driver.save(artifact.to_text())
            output = J2("ramps/storage.j2").render(
                storage_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.config["name"],
                key=key
            )

            return TextArtifact(output)
        else:
            return artifact

    def load_artifact(self, name: str) -> Optional[BaseArtifact]:
        value = self.driver.load(name)

        if value:
            return TextArtifact(value)
        else:
            return ErrorArtifact(f"can't find artifact {name}")

    @activity(config={
        "name": "query_artifact",
        "description": "Can be used to query an artifact in the ramp for any content",
        "schema": Schema({
            Literal(
                "id",
                description="Storage artifact ID"
            ): str,
            Literal(
                "query",
                description="Query to run against the artifact"
            ): str
        })
    })
    def query_artifact(self, value: dict) -> Union[TextArtifact, ErrorArtifact]:
        return self.driver.query_record(value["id"], value['query'])

    @activity(config={
        "name": "summarize_artifact",
        "description": "Can be used to generate a summary of a ramp artifact",
        "schema": Schema(
            str,
            description="Ramp artifact ID"
        )
    })
    def summarize_artifact(self, value: str) -> Union[TextArtifact, ErrorArtifact]:
        return self.driver.summarize_record(value)
