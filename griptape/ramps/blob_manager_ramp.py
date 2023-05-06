import os.path
from typing import Union, Optional
from attr import define, field
from schema import Schema, Literal
from griptape.artifacts import BlobArtifact, BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.ramps import BaseRamp


@define
class BlobManagerRamp(BaseRamp):
    dir: str = field(default=os.getcwd(), kw_only=True)
    blobs: list[BlobArtifact] = field(factory=list, kw_only=True)

    def process_output(self, tool_activity: callable, value: BaseArtifact) -> BaseArtifact:
        if isinstance(value, BlobArtifact):
            from griptape.utils import J2

            self.add_blob(value)

            output = J2("ramps/blob_manager.j2").render(
                blob_manager_name=self.name,
                tool_name=tool_activity.__self__.name,
                activity_name=tool_activity.config["name"],
                full_path=value.full_path
            )

            return TextArtifact(output)
        else:
            return value

    @activity(config={
        "name": "save",
        "description": "Can be used to save blobs on disk",
        "schema": Schema({
            Literal(
                "current_ramp_path",
                description="Current blob path in this ramp"
            ): str,
            Literal(
                "new_disk_path",
                description="Desired blob path on disk"
            ): str
        })
    })
    def save(self, value: dict) -> Union[TextArtifact, ErrorArtifact]:
        current_path = value["current_ramp_path"]
        new_path = value["new_disk_path"]
        blob = self.find_blob(current_path)

        if blob:
            full_path = os.path.join(self.dir, new_path)

            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "wb") as file:
                    file.write(blob.value)

                return TextArtifact(f"Blob was saved to {new_path}")
            except Exception as e:
                return ErrorArtifact(f"error writing blob to disk: {e}")
        else:
            return ErrorArtifact("Blob not found")

    def find_blob(self, full_path: str) -> Optional[BlobArtifact]:
        return next(
            (r for r in self.blobs if r.full_path == full_path),
            None
        )

    def add_blob(self, blob: BlobArtifact) -> None:
        self.blobs = [b for b in self.blobs if b.full_path != blob.full_path]

        self.blobs.append(blob)
