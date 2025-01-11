from __future__ import annotations

import csv
from io import StringIO
from typing import Callable

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.loaders import BaseFileLoader


@define
class CsvLoader(BaseFileLoader[ListArtifact[TextArtifact]]):
    delimiter: str = field(default=",", kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)
    format_row: Callable[[dict], str] = field(
        default=lambda value: "\n".join(f"{key}: {val}" for key, val in value.items()), kw_only=True
    )

    def try_parse(self, data: bytes) -> ListArtifact[TextArtifact]:
        reader = csv.DictReader(StringIO(data.decode(self.encoding)), delimiter=self.delimiter)

        return ListArtifact(
            [TextArtifact(self.format_row(row), meta={"row_num": row_num}) for row_num, row in enumerate(reader)]
        )
