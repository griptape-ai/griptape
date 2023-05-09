from typing import Union, Optional
from attr import define, field
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.ramps import BaseRamp
from griptape.drivers import MemoryTextStorageDriver, BaseTextStorageDriver


@define
class TextManagerRamp(BaseRamp):
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
        return self.driver.load(name)

    @activity(config={
        "name": "query_record",
        "description": "Can be used to query a storage record for any content",
        "schema": Schema({
            Literal(
                "id",
                description="Storage record ID"
            ): str,
            Literal(
                "query",
                description="Query to run against the storage record"
            ): str
        })
    })
    def search_record(self, value: dict) -> Union[TextArtifact, ErrorArtifact]:
        return self.driver.query_record(value["id"], value['query'])

    @activity(config={
        "name": "summarize_record",
        "description": "Can be used to generate a summary of a storage record",
        "schema": Schema(
            str,
            description="Storage record ID"
        )
    })
    def summarize_record(self, value: str) -> Union[TextArtifact, ErrorArtifact]:
        return self.driver.summarize_record(value)
