from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact, BaseArtifact, InfoArtifact, ListArtifact
from griptape.drivers import BaseBlobStorageDriver, MemoryBlobStorageDriver
from griptape.ramps import BaseRamp


@define
class BlobStorageRamp(BaseRamp):
    driver: BaseBlobStorageDriver = field(default=MemoryBlobStorageDriver(), kw_only=True)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        from griptape.utils import J2

        if isinstance(artifact, BlobArtifact):
            artifact_names = [self.driver.save(artifact)]
        elif isinstance(artifact, ListArtifact):
            artifact_names = [self.driver.save(a) for a in artifact.value if isinstance(a, BlobArtifact)]
        else:
            artifact_names = []

        if len(artifact_names) > 0:
            output = J2("ramps/blob_storage.j2").render(
                ramp_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.name,
                names=str.join(", ", artifact_names)
            )

            return InfoArtifact(output)
        else:
            return artifact

    def load_artifact(self, name: str) -> Optional[BaseArtifact]:
        return self.driver.load(name)
