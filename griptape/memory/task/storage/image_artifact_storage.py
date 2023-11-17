from attr import define, field
from griptape.artifacts import ListArtifact, InfoArtifact, ImageArtifact
from griptape.memory.task.storage import BaseArtifactStorage


@define
class ImageArtifactStorage(BaseArtifactStorage):
    images: dict[str, list[ImageArtifact]] = field(factory=dict, kw_only=True)

    def can_store(self, artifact: ImageArtifact) -> bool:
        return isinstance(artifact, ImageArtifact)

    def store_artifact(self, namespace: str, artifact: ImageArtifact) -> None:
        if namespace not in self.images:
            self.images[namespace] = []

        self.images[namespace].append(artifact)

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return ListArtifact(next((images for key, images in self.images.items() if key == namespace), []))

    def summarize(self, namespace: str) -> InfoArtifact:
        return InfoArtifact("can't summarize artifacts")

    def query(self, namespace: str, query: str, metadata: any = None) -> InfoArtifact:
        return InfoArtifact("can't query artifacts")
