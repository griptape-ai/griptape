from __future__ import annotations

import json
from typing import Any, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact

Json = Union[dict[str, "Json"], list["Json"], str, int, float, bool, None]


@define
class JsonArtifact(BaseArtifact):
    _obj: Any = field(metadata={"serializable": True}, alias="obj")
    value: Json = field(init=False, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        self.value = json.loads(json.dumps(self._obj))

    def to_text(self) -> str:
        return json.dumps(self.value)

    def __add__(self, other: BaseArtifact) -> JsonArtifact:
        raise NotImplementedError
