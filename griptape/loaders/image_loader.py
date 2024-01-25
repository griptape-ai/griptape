from __future__ import annotations

import os
from io import BytesIO

from pathlib import Path
from attr import define, field
from PIL import Image

from griptape import utils
from griptape.artifacts import ImageArtifact
from griptape.loaders import BaseLoader


@define
class ImageLoader(BaseLoader):
    """Loader for images.

    Attributes:
        format: Attempt to ensure image artifacts are in this format when loaded. For example, when set to 'PNG',
            loading image.jpg will return an ImageArtifact contianing the image bytes in PNG format.
            Defaults to PNG.
    """

    format: str = field(default="PNG", kw_only=True)

    def load(self, source: str | Path, *args, **kwargs) -> ImageArtifact:
        return self.file_to_artifact(source)

    def load_collection(self, sources: list[str | Path], *args, **kwargs) -> dict[str, ImageArtifact]:
        return utils.execute_futures_dict(
            {utils.str_to_hash(str(source)): self.futures_executor.submit(self.file_to_artifact, source) for source in sources}
        )

    def file_to_artifact(self, path: str | Path) -> ImageArtifact:
        file_name = os.path.basename(path)
        dir_name = os.path.dirname(path)

        image = Image.open(path)

        # Ensure image is in the specified format.
        byte_stream = BytesIO()
        image.save(byte_stream, format=self.format)

        return ImageArtifact(
            byte_stream.getvalue(),
            name=file_name,
            dir_name=dir_name,
            mime_type=f"image/{self.format.lower()}",
            width=image.width,
            height=image.height,
        )
