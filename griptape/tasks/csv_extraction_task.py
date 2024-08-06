from __future__ import annotations

from attrs import Factory, define, field

from griptape.engines import CsvExtractionEngine
from griptape.tasks import ExtractionTask


@define
class CsvExtractionTask(ExtractionTask):
    extraction_engine: CsvExtractionEngine = field(default=Factory(lambda: CsvExtractionEngine()), kw_only=True)
