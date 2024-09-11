from __future__ import annotations

import json
from typing import Any, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact

Json = Union[dict[str, "Json"], list["Json"], str, int, float, bool, None]


@define
class JsonArtifact(BaseArtifact):
    """Stores JSON data.

    Attributes:
        value: The JSON data. Values will automatically be converted to a JSON-compatible format.
    """

    value: Json = field(converter=lambda value: JsonArtifact.value_to_json(value), metadata={"serializable": True})

    @classmethod
    def value_to_json(cls, value: Any) -> Json:
        if isinstance(value, str):
            return json.loads(value)
        else:
            return json.loads(json.dumps(value))

    def to_text(self) -> str:
        return json.dumps(self.value)
