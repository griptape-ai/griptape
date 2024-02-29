from __future__ import annotations

import os
from typing import Optional

from pathlib import Path
from attr import define, field

from griptape import utils
from griptape.artifacts import BlobArtifact, TextArtifact, ErrorArtifact
from griptape.loaders import BaseLoader


@define
class FileLoader(BaseLoader):
    encoding: Optional[str] = field(default=None, kw_only=True)

    def load(self, source: str | Path, *args, **kwargs) -> TextArtifact | BlobArtifact | ErrorArtifact:
        return self.file_to_artifact(source)

    def load_collection(
        self, sources: list[str | Path], *args, **kwargs
    ) -> dict[str, TextArtifact | BlobArtifact | ErrorArtifact]:
        return utils.execute_futures_dict(
            {
                utils.str_to_hash(str(source)): self.futures_executor.submit(self.file_to_artifact, source)
                for source in sources
            }
        )

    def file_to_artifact(self, path: str | Path) -> TextArtifact | BlobArtifact | ErrorArtifact:
        file_name = os.path.basename(path)

        try:
            with open(path, "rb") as file:
                if self.encoding:
                    return TextArtifact(file.read().decode(self.encoding), name=file_name)
                else:
                    return BlobArtifact(file.read(), name=file_name, dir_name=os.path.dirname(path))
        except FileNotFoundError:
            return ErrorArtifact(f"file {file_name} not found")
        except Exception as e:
            return ErrorArtifact(f"error loading file: {e}")
