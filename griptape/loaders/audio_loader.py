from __future__ import annotations

import filetype
from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.loaders.base_file_loader import BaseFileLoader


@define
class AudioLoader(BaseFileLoader[AudioArtifact]):
    """Loads audio content into audio artifacts."""

    def parse(self, source: bytes) -> AudioArtifact:
        return AudioArtifact(source, format=filetype.guess(source).extension)
