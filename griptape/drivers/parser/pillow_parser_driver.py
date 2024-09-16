from __future__ import annotations

from io import BytesIO
from typing import Optional

from attrs import define, field

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseParserDriver
from griptape.utils import import_optional_dependency


@define
class PillowParserDriver(BaseParserDriver[ImageArtifact]):
    format: Optional[str] = field(default=None, kw_only=True)

    def try_parse(self, data: bytes, meta: dict) -> ImageArtifact:
        pil_image = import_optional_dependency("PIL.Image")
        image = pil_image.open(BytesIO(data))

        # Normalize format only if requested.
        if self.format is not None:
            byte_stream = BytesIO()
            image.save(byte_stream, format=self.format)
            image = pil_image.open(byte_stream)
            data = byte_stream.getvalue()

        return ImageArtifact(data, format=image.format.lower(), width=image.width, height=image.height)
