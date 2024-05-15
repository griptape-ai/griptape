from __future__ import annotations

from typing import TYPE_CHECKING, cast

from attr import define

from griptape.artifacts import AudioArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    pass


@define
class AudioLoader(BaseLoader):
    """Loads audio content into audio artifacts."""

    FORMAT_TO_MIME_TYPE = {}

    def load(self, source: bytes, *args, **kwargs) -> AudioArtifact:
        audio_artifact = AudioArtifact(source, format="wav")

        return audio_artifact

    # def _get_mime_type(self, image_format: str | None) -> str:
    #     if image_format is None:
    #         raise ValueError("image_format is None")
    #
    #     if image_format.lower() not in self.FORMAT_TO_MIME_TYPE:
    #         raise ValueError(f"Unsupported image format {image_format}")
    #
    #     return self.FORMAT_TO_MIME_TYPE[image_format.lower()]

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, AudioArtifact]:
        return cast(dict[str, AudioArtifact], super().load_collection(sources, *args, **kwargs))
