from attr import define, field
from griptape.artifacts import BaseArtifact, ListArtifact, BlobArtifact, InfoArtifact
from griptape.memory.tool.storage import BaseToolMemoryStorage


@define
class BlobToolMemoryStorage(BaseToolMemoryStorage):
    blobs: dict[str, list[BlobArtifact]] = field(factory=dict, kw_only=True)

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, BlobArtifact)

    def store_artifact(self, namespace: str, artifact: BlobArtifact) -> None:
        if namespace not in self.blobs:
            self.blobs[namespace] = []

        self.blobs[namespace].append(artifact)

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return ListArtifact(
            next(
                (blobs for key, blobs in self.blobs.items() if key == namespace),
                []
            )
        )

    def summarize(self, namespace: str) -> InfoArtifact:
        return InfoArtifact("Can't summarize artifacts")
