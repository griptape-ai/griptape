from __future__ import annotations

from attrs import define

from griptape.artifacts import AudioArtifact
from griptape.drivers import BaseParserDriver


@define
class AudioParserDriver(BaseParserDriver[AudioArtifact]):
    def try_parse(self, data: bytes, meta: dict) -> AudioArtifact:
        return AudioArtifact(data, format=meta["mime_type"].split("/")[-1])
