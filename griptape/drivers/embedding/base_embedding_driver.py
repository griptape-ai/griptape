import logging
from abc import ABC, abstractmethod
from tenacity import Retrying, wait_exponential, after_log
from attr import define, field
from griptape.artifacts import TextArtifact


@define
class BaseEmbeddingDriver(ABC):
    dimensions: int = field(kw_only=True)
    min_retry_delay: float = field(default=2, kw_only=True)
    max_retry_delay: float = field(default=10, kw_only=True)

    def embed_text_artifact(self, artifact: TextArtifact) -> list[float]:
        return self.embed_string(artifact.to_text())

    def embed_string(self, string: str) -> list[float]:
        for attempt in Retrying(
                wait=wait_exponential(
                    min=self.min_retry_delay,
                    max=self.max_retry_delay
                ),
                reraise=True,
                after=after_log(
                    logger=logging.getLogger(__name__),
                    log_level=logging.ERROR
                )
        ):
            with attempt:
                return self.try_embed_string(string)

    @abstractmethod
    def try_embed_string(self, string: str) -> list[float]:
        ...
    