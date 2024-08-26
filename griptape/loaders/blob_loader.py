from __future__ import annotations

from typing import Any, cast

from attrs import define

from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseLoader


@define
class BlobLoader(BaseLoader):
    def load(self, source: Any, *args, **kwargs) -> BlobArtifact:
        if self.encoding is None:
            return BlobArtifact(source)
        else:
            return BlobArtifact(source, encoding=self.encoding)

    def load_collection(self, sources: list[bytes | str], *args, **kwargs) -> dict[str, BlobArtifact]:
        return cast(dict[str, BlobArtifact], super().load_collection(sources, *args, **kwargs))
