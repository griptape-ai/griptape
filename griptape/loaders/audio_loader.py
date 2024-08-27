from __future__ import annotations

from typing import Any, cast

import filetype
from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.loaders.base_file_loader import BaseFileLoader


@define
class AudioLoader(BaseFileLoader):
    """Loads audio content into audio artifacts."""

    def load(self, source: Any, *args, **kwargs) -> AudioArtifact:
        return cast(AudioArtifact, super().load(source, *args, **kwargs))

    def parse(self, source: bytes, *args, **kwargs) -> AudioArtifact:
        return AudioArtifact(source, format=filetype.guess(source).extension)
