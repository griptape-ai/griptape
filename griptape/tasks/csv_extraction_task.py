from __future__ import annotations

from attrs import Factory, define, field

from griptape.tasks import ExtractionTask

if TYPE_CHECKING:
    from griptape.engines import CsvExtractionEngine


@define
class CsvExtractionTask(ExtractionTask):
    extraction_engine: CsvExtractionEngine = field(default=Factory(lambda: CsvExtractionEngine()), kw_only=True)
