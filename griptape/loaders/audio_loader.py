from __future__ import annotations

import filetype
from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.loaders.base_file_loader import BaseFileLoader


@define
class AudioLoader(BaseFileLoader[AudioArtifact]):
    """Loads audio content into audio artifacts."""

    def try_parse(self, data: bytes) -> AudioArtifact:
        filetype_guess = filetype.guess(data)
        if filetype_guess is None:
            raise ValueError("Could not determine the file type of the audio data")
        return AudioArtifact(data, format=filetype_guess.extension)
