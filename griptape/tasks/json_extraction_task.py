from __future__ import annotations

from attrs import Factory, define, field

from griptape.tasks import ExtractionTask

if TYPE_CHECKING:
    from griptape.engines import JsonExtractionEngine


@define
class JsonExtractionTask(ExtractionTask):
    extraction_engine: JsonExtractionEngine = field(default=Factory(lambda: JsonExtractionEngine()), kw_only=True)
