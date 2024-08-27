from __future__ import annotations

from typing import Any, cast

from attrs import define

from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseFileLoader


@define
class BlobLoader(BaseFileLoader):
    def load(self, source: Any, *args, **kwargs) -> BlobArtifact:
        return cast(BlobArtifact, super().load(source, *args, **kwargs))

    def parse(self, source: bytes, *args, **kwargs) -> BlobArtifact:
        if self.encoding is None:
            return BlobArtifact(source)
        else:
            return BlobArtifact(source, encoding=self.encoding)
