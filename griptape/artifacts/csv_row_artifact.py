from __future__ import annotations

import csv
import io

from attrs import define, field

from griptape.artifacts import BaseArtifact, BaseTextArtifact


@define
class CsvRowArtifact(BaseTextArtifact):
    value: dict[str, str] = field(converter=BaseArtifact.value_to_dict, metadata={"serializable": True})
    delimiter: str = field(default=",", kw_only=True, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> CsvRowArtifact:
        return CsvRowArtifact(self.value | other.value)

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_text(self) -> str:
        with io.StringIO() as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.value.keys(),
                quoting=csv.QUOTE_MINIMAL,
                delimiter=self.delimiter,
            )

            writer.writerow(self.value)

            return csvfile.getvalue().strip()
