from __future__ import annotations

from attrs import define

from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseFileLoader


@define
class BlobLoader(BaseFileLoader[BlobArtifact]):
    def parse(self, source: bytes, *args, **kwargs) -> BlobArtifact:
        if self.encoding is None:
            return BlobArtifact(source)
        else:
            return BlobArtifact(source, encoding=self.encoding)
