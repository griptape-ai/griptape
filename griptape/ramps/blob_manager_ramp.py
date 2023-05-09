from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact, BaseArtifact, TextArtifact
from griptape.drivers import BaseBlobStorageDriver, MemoryBlobStorageDriver
from griptape.ramps import BaseRamp
from griptape.schemas import BlobArtifactSchema


@define
class BlobManagerRamp(BaseRamp):
    driver: BaseBlobStorageDriver = field(default=MemoryBlobStorageDriver(), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        record_names = []

        if value:
            sources = value.get("records", {}).get("sources", [])

            for source in sources:
                if source["ramp_name"] == self.name:
                    record_names.extend(source["record_names"])

        if len(record_names) > 0:
            new_value = value.copy()

            new_value.update({"records": {"values": []}})

            for artifact_name in record_names:
                new_value["records"]["values"].append(
                    dict(BlobArtifactSchema().dump(self.driver.load(artifact_name)))
                )

            return new_value
        else:
            return value

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        if isinstance(artifact, BlobArtifact):
            from griptape.utils import J2

            self.driver.save(artifact)

            output = J2("ramps/blob_manager.j2").render(
                blob_manager_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.config["name"],
                full_path=artifact.full_path
            )

            return TextArtifact(output)
        else:
            return artifact
