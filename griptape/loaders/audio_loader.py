from __future__ import annotations

import filetype
from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.loaders.base_file_loader import BaseFileLoader


@define
class AudioLoader(BaseFileLoader[AudioArtifact]):
    """Loads audio content into audio artifacts."""

    def parse(self, data: bytes) -> AudioArtifact:
        return AudioArtifact(data, format=filetype.guess(data).extension)
