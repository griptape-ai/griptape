from __future__ import annotations

from io import BufferedIOBase, BytesIO, RawIOBase
from pathlib import Path
from typing import IO, Any, Optional, TYPE_CHECKING, cast
from collections.abc import Sequence

from attr import define, field

from griptape.utils import import_optional_dependency
from griptape.artifacts import ImageArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    import PIL.Image as Image


@define
class ImageLoader(BaseLoader):
    """Loads images into image artifacts.

    Attributes:
        format: If provided, attempts to ensure image artifacts are in this format when loaded.
                For example, when set to 'PNG', loading image.jpg will return an ImageArtifact containing the image
                    bytes in PNG format.
    """

    format: Optional[str] = field(default=None, kw_only=True)

    FORMAT_TO_MIME_TYPE = {
        "bmp": "image/bmp",
        "gif": "image/gif",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "tiff": "image/tiff",
        "webp": "image/webp",
    }

    def load(self, source: bytes | IO | Path, *args, **kwargs) -> ImageArtifact:
        with self._stream_from_source(source) as stream:
            Image = import_optional_dependency("PIL.Image")
            image = Image.open(stream)

            # Normalize format only if requested.
            if self.format is not None:
                byte_stream = BytesIO()
                image.save(byte_stream, format=self.format)
                image = Image.open(byte_stream)
                source = byte_stream.getvalue()

            image_artifact = ImageArtifact(
                source, mime_type=self._get_mime_type(image.format), width=image.width, height=image.height
            )

            return image_artifact

    def _stream_from_source(self, source: bytes | IO | Path) -> IO:
        if isinstance(source, bytes):
            return BytesIO(source)
        elif isinstance(source, str):
            return open(source, "rb")
        elif isinstance(source, (RawIOBase, BufferedIOBase)):
            return cast(IO, source)
        elif isinstance(source, Path):
            return open(source, "rb")
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def _get_mime_type(self, image_format: str | None) -> str:
        if image_format is None:
            raise ValueError("image_format is None")

        if image_format.lower() not in self.FORMAT_TO_MIME_TYPE:
            raise ValueError(f"Unsupported image format {image_format}")

        return self.FORMAT_TO_MIME_TYPE[image_format.lower()]

    def load_collection(self, sources: Sequence[bytes | IO | Path], *args, **kwargs) -> dict[str, ImageArtifact]:
        return cast(Any, super().load_collection(sources, *args, **kwargs))
