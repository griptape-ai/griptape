from __future__ import annotations
from attr import define, field
from griptape.artifacts import TextArtifact


@define(frozen=True)
class CsvRowArtifact(TextArtifact):
    value: dict[str, any] = field()
    separator: str = field(default=",", kw_only=True)

    def __add__(self, other: CsvRowArtifact) -> CsvRowArtifact:
        return CsvRowArtifact(self.value | other.value)

    def to_text(self) -> str:
        return self.separator.join([v for v in self.value.values()])

    def to_dict(self) -> dict:
        from griptape.schemas import CsvRowArtifactSchema

        return dict(CsvRowArtifactSchema().dump(self))
