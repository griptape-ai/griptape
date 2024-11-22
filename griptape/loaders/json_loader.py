from __future__ import annotations

import json

from attrs import define

from griptape.artifacts import JsonArtifact
from griptape.loaders import BaseFileLoader


@define
class JsonLoader(BaseFileLoader[JsonArtifact]):
    def parse(self, data: bytes) -> JsonArtifact:
        return JsonArtifact(json.loads(data), encoding=self.encoding)
