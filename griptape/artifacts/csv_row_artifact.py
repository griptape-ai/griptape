from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact


def value_to_str(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"{key}: {val}" for key, val in value.items())
    else:
        return str(value)


@define
class CsvRowArtifact(TextArtifact):
    """Stores a row of a CSV file.

    Attributes:
        value: The row of the CSV file. If a dictionary is passed, the keys and values converted to a string.
    """

    value: str = field(converter=value_to_str, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> TextArtifact:
        return TextArtifact(self.value + "\n" + other.value)
