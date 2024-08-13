from __future__ import annotations

from attrs import Factory, define, field

from griptape.engines import JsonExtractionEngine
from griptape.tasks import ExtractionTask


@define
class JsonExtractionTask(ExtractionTask):
    extraction_engine: JsonExtractionEngine = field(default=Factory(lambda: JsonExtractionEngine()), kw_only=True)
