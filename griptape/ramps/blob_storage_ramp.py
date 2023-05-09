from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact, BaseArtifact, InfoArtifact
from griptape.drivers import BaseBlobStorageDriver, MemoryBlobStorageDriver
from griptape.ramps import BaseRamp


@define
class BlobStorageRamp(BaseRamp):
    driver: BaseBlobStorageDriver = field(default=MemoryBlobStorageDriver(), kw_only=True)

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

            return InfoArtifact(output)
        else:
            return artifact

    def load_artifact(self, name: str) -> Optional[BaseArtifact]:
        return self.driver.load(name)
