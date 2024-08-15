from __future__ import annotations

import json
from typing import Union

from attrs import define, field

from griptape.artifacts import BaseArtifact

Json = Union[dict[str, "Json"], list["Json"], str, int, float, bool, None]


@define
class JsonArtifact(BaseArtifact):
    value: Json = field(converter=lambda v: json.loads(json.dumps(v)), metadata={"serializable": True})

    def to_text(self) -> str:
        return json.dumps(self.value)

    def __add__(self, other: BaseArtifact) -> JsonArtifact:
        raise NotImplementedError
