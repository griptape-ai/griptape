from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact, BlobArtifact, InfoArtifact, ListArtifact
from griptape.memory.task.storage import BaseArtifactStorage


@define
class BlobArtifactStorage(BaseArtifactStorage):
    blobs: dict[str, list[BlobArtifact]] = field(factory=dict, kw_only=True)

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, BlobArtifact)

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        if isinstance(artifact, BlobArtifact):
            if namespace not in self.blobs:
                self.blobs[namespace] = []

            self.blobs[namespace].append(artifact)
        else:
            raise ValueError("Artifact must be of instance BlobArtifact")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return ListArtifact(next((blobs for key, blobs in self.blobs.items() if key == namespace), []))

    def summarize(self, namespace: str) -> InfoArtifact:
        return InfoArtifact("can't summarize artifacts")

    def query(self, namespace: str, query: str, metadata: Any = None) -> BaseArtifact:
        return InfoArtifact("can't query artifacts")
