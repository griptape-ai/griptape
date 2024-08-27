from abc import ABC

from griptape.artifacts import BaseArtifact


class BaseSystemArtifact(BaseArtifact, ABC):
    """Serves as the base class for all Artifacts specific to Griptape."""

    def to_text(self) -> str:
        return self.value
