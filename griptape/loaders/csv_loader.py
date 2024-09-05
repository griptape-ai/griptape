from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING, Callable, Optional, cast

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.loaders.base_file_loader import BaseFileLoader


@define
class CsvLoader(BaseFileLoader[ListArtifact]):
    delimiter: str = field(default=",", kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)
    formatter_fn: Callable[[dict], str] = field(
        default=lambda value: "\n".join(f"{key}: {val}" for key, val in value.items()), kw_only=True
    )

    def parse(self, data: bytes) -> ListArtifact:
        reader = csv.DictReader(StringIO(data.decode(self.encoding)), delimiter=self.delimiter)

        return ListArtifact([TextArtifact(row, meta={"row": row_num}) for row_num, row in enumerate(reader)])
