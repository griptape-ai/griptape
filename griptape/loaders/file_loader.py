from __future__ import annotations

import os
from typing import Any, Optional, cast
from collections.abc import Sequence

from pathlib import Path
from attr import define, field

from griptape.artifacts import BlobArtifact, TextArtifact, ErrorArtifact
from griptape.loaders import BaseLoader


@define
class FileLoader(BaseLoader):
    encoding: Optional[str] = field(default=None, kw_only=True)

    def load(self, source: str | Path, *args, **kwargs) -> TextArtifact | BlobArtifact | ErrorArtifact:
        file_name = os.path.basename(source)

        try:
            with open(source, "rb") as file:
                if self.encoding:
                    return TextArtifact(file.read().decode(self.encoding), name=file_name)
                else:
                    return BlobArtifact(file.read(), name=file_name, dir_name=os.path.dirname(source))
        except FileNotFoundError:
            return ErrorArtifact(f"file {file_name} not found")
        except Exception as e:
            return ErrorArtifact(f"error loading file: {e}")

    def load_collection(
        self, sources: Sequence[str | Path], *args, **kwargs
    ) -> dict[str, TextArtifact | BlobArtifact | ErrorArtifact]:
        return cast(Any, super().load_collection(sources, *args, **kwargs))
