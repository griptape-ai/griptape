from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact
from griptape.drivers import BaseBlobStorageDriver


@define
class MemoryBlobStorageDriver(BaseBlobStorageDriver):
    blobs: list[BlobArtifact] = field(factory=list, kw_only=True)

    def save(self, blob: BlobArtifact) -> str:
        self.blobs = [b for b in self.blobs if b.full_path != blob.full_path]

        self.blobs.append(blob)

        return blob.full_path

    def load(self, key: str) -> Optional[BlobArtifact]:
        return next(
            (r for r in self.blobs if r.full_path == key),
            None
        )

    def delete(self, key: str) -> None:
        blob = self.load(key)

        if blob:
            self.blobs.remove(blob)