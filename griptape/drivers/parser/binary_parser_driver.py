from __future__ import annotations

from attrs import define

from griptape.artifacts.blob_artifact import BlobArtifact
from griptape.drivers import BaseParserDriver


@define
class BinaryParserDriver(BaseParserDriver[BlobArtifact]):
    def try_parse(self, data: bytes, meta: dict) -> BlobArtifact:
        return BlobArtifact(data)
