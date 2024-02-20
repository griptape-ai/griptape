from __future__ import annotations

from io import BytesIO
from typing import Optional, TYPE_CHECKING

from attr import define, field

from griptape.utils import execute_futures_dict, str_to_hash, import_optional_dependency
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

    def load(self, source: bytes, *args, **kwargs) -> ImageArtifact:
        return self._load(source)

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, ImageArtifact]:
        return execute_futures_dict(
            {str_to_hash(str(source)): self.futures_executor.submit(self._load, source) for source in sources}
        )

    def _load(self, source: bytes) -> ImageArtifact:
        Image = import_optional_dependency("PIL.Image")
        image = Image.open(BytesIO(source))

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

    def _get_mime_type(self, image_format: str | None) -> str:
        if image_format is None:
            raise ValueError("image_format is None")

        if image_format.lower() not in self.FORMAT_TO_MIME_TYPE:
            raise ValueError(f"Unsupported image format {image_format}")

        return self.FORMAT_TO_MIME_TYPE[image_format.lower()]
