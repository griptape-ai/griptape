from __future__ import annotations

from attrs import define

from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseFileLoader


@define
class BlobLoader(BaseFileLoader[BlobArtifact]):
    def try_parse(self, data: bytes) -> BlobArtifact:
        if self.encoding is None:
            return BlobArtifact(data)
        else:
            return BlobArtifact(data, encoding=self.encoding)
