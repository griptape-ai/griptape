from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts.text_artifact import TextArtifact

if TYPE_CHECKING:
    from collections.abc import Sequence


@define
class TableArtifact(TextArtifact):
    value: list[dict] = field(factory=list, metadata={"serializable": True})
    delimiter: str = field(default=",", kw_only=True, metadata={"serializable": True})
    fieldnames: Optional[Sequence[str]] = field(factory=list, metadata={"serializable": True})
    quoting: int = field(default=csv.QUOTE_MINIMAL, kw_only=True, metadata={"serializable": True})
    line_terminator: str = field(default="\n", kw_only=True, metadata={"serializable": True})

    def __bool__(self) -> bool:
        return len(self.value) > 0

    def to_text(self) -> str:
        with io.StringIO() as csvfile:
            fieldnames = (self.value[0].keys() if self.value else []) if self.fieldnames is None else self.fieldnames

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                quoting=self.quoting,
                delimiter=self.delimiter,
                lineterminator=self.line_terminator,
            )

            writer.writeheader()
            writer.writerows(self.value)

            return csvfile.getvalue().strip()
