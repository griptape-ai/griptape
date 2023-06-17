from attr import define, field
from griptape.artifacts import BlobArtifact
from griptape.drivers import BaseBlobToolMemoryDriver


@define
class LocalBlobToolMemoryDriver(BaseBlobToolMemoryDriver):
    blobs: dict[str, list[BlobArtifact]] = field(factory=dict, kw_only=True)

    def save(self, namespace: str, blob: BlobArtifact) -> None:
        if namespace not in self.blobs:
            self.blobs[namespace] = []

        self.blobs[namespace].append(blob)

    def load(self, namespace: str) -> list[BlobArtifact]:
        return next(
            (blobs for key, blobs in self.blobs.items() if key == namespace),
            []
        )

    def delete(self, namespace: str) -> None:
        if namespace in self.blobs:
            self.blobs.pop(namespace)
