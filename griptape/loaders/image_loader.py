from __future__ import annotations

from io import BytesIO
from typing import Optional, cast

from attrs import define, field

from griptape.artifacts import ImageArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency


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
        pil_image = import_optional_dependency("PIL.Image")
        image = pil_image.open(BytesIO(source))

        # Normalize format only if requested.
        if self.format is not None:
            byte_stream = BytesIO()
            image.save(byte_stream, format=self.format)
            image = pil_image.open(byte_stream)
            source = byte_stream.getvalue()

        image_artifact = ImageArtifact(source, format=image.format.lower(), width=image.width, height=image.height)

        return image_artifact

    def _get_mime_type(self, image_format: str | None) -> str:
        if image_format is None:
            raise ValueError("image_format is None")

        if image_format.lower() not in self.FORMAT_TO_MIME_TYPE:
            raise ValueError(f"Unsupported image format {image_format}")

        return self.FORMAT_TO_MIME_TYPE[image_format.lower()]

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, ImageArtifact]:
        return cast(dict[str, ImageArtifact], super().load_collection(sources, *args, **kwargs))
