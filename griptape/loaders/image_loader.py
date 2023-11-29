from __future__ import annotations
import os
from io import BytesIO
from pathlib import Path
from attr import define
from griptape import utils
from griptape.artifacts import ImageArtifact, ErrorArtifact
from griptape.loaders import BaseLoader
from PIL import Image


@define
class ImageLoader(BaseLoader):
    def load(self, path: str | Path) -> ImageArtifact | ErrorArtifact:
        return self.file_to_artifact(path)

    def load_collection(self, paths: list[str | Path]) -> dict[str, ImageArtifact | ErrorArtifact]:
        return utils.execute_futures_dict(
            {utils.str_to_hash(str(path)): self.futures_executor.submit(self.file_to_artifact, path) for path in paths}
        )

    def file_to_artifact(self, path: str | Path) -> ImageArtifact | ErrorArtifact:
        file_name = os.path.basename(path)
        dir_name = os.path.dirname(path)

        try:
            image = Image.open(path)

            # Ensure image is in png format.
            byte_stream = BytesIO()
            image.save(byte_stream, format="png")

            return ImageArtifact(
                byte_stream.getvalue(),
                name=file_name,
                dir_name=dir_name,
                mime_type="image/png",
                width=image.width,
                height=image.height,
            )

        except FileNotFoundError:
            return ErrorArtifact(f"file {file_name} not found")

        except Exception as e:
            return ErrorArtifact(f"error loading file: {e}")
