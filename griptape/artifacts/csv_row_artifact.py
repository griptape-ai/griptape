from __future__ import annotations
import csv
import io
from attr import define, field
from griptape.artifacts import TextArtifact, BaseArtifact


@define(frozen=True)
class CsvRowArtifact(TextArtifact):
    value: dict[str, str] = field(converter=BaseArtifact.value_to_dict)
    delimiter: str = field(default=",", kw_only=True)

    def __add__(self, other: CsvRowArtifact) -> CsvRowArtifact:
        return CsvRowArtifact(self.value | other.value)

    def to_text(self) -> str:
        with io.StringIO() as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=self.value.keys(), quoting=csv.QUOTE_MINIMAL, delimiter=self.delimiter
            )

            writer.writerow(self.value)

            return csvfile.getvalue().strip()

    def to_dict(self) -> dict:
        from griptape.schemas import CsvRowArtifactSchema

        return dict(CsvRowArtifactSchema().dump(self))

    def __bool__(self) -> bool:
        return len(self) > 0
