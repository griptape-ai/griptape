from __future__ import annotations

import json

from attrs import define

from griptape.artifacts import JsonArtifact
from griptape.loaders import BaseFileLoader


@define
class JsonLoader(BaseFileLoader[JsonArtifact]):
    def parse(self, data: bytes) -> JsonArtifact:
        value = json.loads(data)
        # JsonArtifact treats string arguments as serialized JSON.
        return JsonArtifact(json.dumps(value) if isinstance(value, str) else value, encoding=self.encoding)
