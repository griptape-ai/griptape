from __future__ import annotations

from typing import cast

from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency


@define
class AudioLoader(BaseLoader):
    """Loads audio content into audio artifacts."""

    def load(self, source: bytes, *args, **kwargs) -> AudioArtifact:
        audio_artifact = AudioArtifact(source, format=import_optional_dependency("filetype").guess(source).extension)

        return audio_artifact

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, AudioArtifact]:
        return cast(dict[str, AudioArtifact], super().load_collection(sources, *args, **kwargs))
