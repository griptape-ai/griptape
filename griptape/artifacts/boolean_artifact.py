from __future__ import annotations

from typing import Union

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class BooleanArtifact(BaseArtifact):
    """Stores a boolean value.

    Attributes:
        value: The boolean value.
    """

    value: bool = field(converter=bool, metadata={"serializable": True})

    @classmethod
    def parse_bool(cls, value: Union[str, bool]) -> BooleanArtifact:
        """Convert a string literal or bool to a BooleanArtifact. The string must be either "true" or "false"."""
        if value is not None:
            if isinstance(value, str):
                if value.lower() == "true":
                    return BooleanArtifact(value=True)
                elif value.lower() == "false":
                    return BooleanArtifact(value=False)
            elif isinstance(value, bool):
                return BooleanArtifact(value)
        raise ValueError(f"Cannot convert '{value}' to BooleanArtifact")

    def __add__(self, other: BaseArtifact) -> BooleanArtifact:
        raise ValueError("Cannot add BooleanArtifact with other artifacts")

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def to_text(self) -> str:
        return str(self.value).lower()
