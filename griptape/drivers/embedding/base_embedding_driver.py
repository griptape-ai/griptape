from abc import ABC, abstractmethod
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.mixins import ExponentialBackoffMixin


@define
class BaseEmbeddingDriver(ExponentialBackoffMixin, ABC):
    dimensions: int = field(kw_only=True)

    def embed_text_artifact(self, artifact: TextArtifact) -> list[float]:
        return self.embed_string(artifact.to_text())

    def embed_string(self, string: str) -> list[float]:
        for attempt in self.retrying():
            with attempt:
                return self.try_embed_string(string)

    @abstractmethod
    def try_embed_string(self, string: str) -> list[float]:
        ...
    