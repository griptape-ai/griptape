from __future__ import annotations

import json
from typing import Any, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact

Json = Union[dict[str, "Json"], list["Json"], str, int, float, bool, None]


@define
class JsonArtifact(BaseArtifact):
    _obj: Any = field(metadata={"serializable": True}, alias="obj")
    value: dict = field(init=False, metadata={"serializable": True})
    _json_str: str = field(init=False, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        if self._obj is None:
            self._obj = {}
        self._json_str = json.dumps(self._obj)
        self.value = json.loads(self._json_str)

    def to_text(self) -> str:
        return self._json_str

    def __add__(self, other: BaseArtifact) -> JsonArtifact:
        if not isinstance(other, JsonArtifact):
            raise ValueError(f"Cannot add {type(self)} and {type(other)}")

        from griptape.utils import dict_merge

        self.value = dict_merge(self.value, other.value)
        return self
