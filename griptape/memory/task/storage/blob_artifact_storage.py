from attr import define, field
from griptape.artifacts import BaseArtifact, ListArtifact, BlobArtifact, InfoArtifact
from griptape.memory.task.storage import BaseArtifactStorage


@define
class BlobArtifactStorage(BaseArtifactStorage):
    blobs: dict[str, list[BlobArtifact]] = field(factory=dict, kw_only=True)

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, BlobArtifact)

    def store_artifact(self, namespace: str, artifact: BlobArtifact) -> None:
        if namespace not in self.blobs:
            self.blobs[namespace] = []

        self.blobs[namespace].append(artifact)

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return ListArtifact(next((blobs for key, blobs in self.blobs.items() if key == namespace), []))

    def summarize(self, namespace: str) -> InfoArtifact:
        return InfoArtifact("can't summarize artifacts")

    def query(self, namespace: str, query: str, metadata: any = None) -> InfoArtifact:
        return InfoArtifact("can't query artifacts")
