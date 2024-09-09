from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact


@define
class CsvRowArtifact(TextArtifact):
    """Stores a row of a CSV file.

    Attributes:
        value: The row of the CSV file. If a dictionary is passed, the keys and values converted to a string.
    """

    value: str = field(converter=lambda value: CsvRowArtifact.value_to_str(value), metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> TextArtifact:
        return TextArtifact(self.value + "\n" + other.value)

    @classmethod
    def value_to_str(cls, value: Any) -> str:
        if isinstance(value, dict):
            return "\n".join(f"{key}: {val}" for key, val in value.items())
        else:
            return str(value)
