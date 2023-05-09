from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact, BaseArtifact, TextArtifact
from griptape.ramps import BaseRamp
from griptape.schemas import BlobArtifactSchema


@define
class BlobManagerRamp(BaseRamp):
    blobs: list[BlobArtifact] = field(factory=list, kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        artifact_names = []

        if value:
            sources = value.get("artifacts", {}).get("sources", [])

            for source in sources:
                if source["ramp_name"] == self.name:
                    artifact_names.extend(source["artifact_names"])

        if len(artifact_names) > 0:
            new_value = value.copy()

            new_value.update({"artifacts": {"values": []}})

            for artifact_name in artifact_names:
                new_value["artifacts"]["values"].append(
                    dict(BlobArtifactSchema().dump(self.find_blob(artifact_name)))
                )

            return new_value
        else:
            return value

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

    def find_blob(self, full_path: str) -> Optional[BlobArtifact]:
        return next(
            (r for r in self.blobs if r.full_path == full_path),
            None
        )

    def add_blob(self, blob: BlobArtifact) -> None:
        self.blobs = [b for b in self.blobs if b.full_path != blob.full_path]

        self.blobs.append(blob)
