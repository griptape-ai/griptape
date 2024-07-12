from __future__ import annotations

from typing import Any, Union, cast

from attrs import define

from griptape.artifacts import BlobArtifact, ErrorArtifact
from griptape.loaders import BaseLoader


@define
class BlobLoader(BaseLoader):
    def load(self, source: Any, *args, **kwargs) -> BlobArtifact | ErrorArtifact:
        if self.encoding is None:
            return BlobArtifact(source)
        else:
            return BlobArtifact(source, encoding=self.encoding)

    def load_collection(self, sources: list[bytes | str], *args, **kwargs) -> dict[str, BlobArtifact | ErrorArtifact]:
        return cast(dict[str, Union[BlobArtifact, ErrorArtifact]], super().load_collection(sources, *args, **kwargs))
