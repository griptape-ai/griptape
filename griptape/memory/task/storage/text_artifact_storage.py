from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact
from griptape.configs import Defaults
from griptape.memory.task.storage import BaseArtifactStorage

if TYPE_CHECKING:
    from griptape.drivers import BaseVectorStoreDriver


@define(kw_only=True)
class TextArtifactStorage(BaseArtifactStorage):
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda: Defaults.drivers_config.vector_store_driver)
    )

    def can_store(self, artifact: BaseArtifact) -> bool:
        return isinstance(artifact, TextArtifact)

    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        if isinstance(artifact, TextArtifact):
            self.vector_store_driver.upsert_text_artifact(artifact, namespace=namespace)
        else:
            raise ValueError("Artifact must be of instance TextArtifact")

    def load_artifacts(self, namespace: str) -> ListArtifact:
        return self.vector_store_driver.load_artifacts(namespace=namespace)
