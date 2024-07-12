from __future__ import annotations

from attrs import define, field

from griptape.engines import CsvExtractionEngine
from griptape.tasks import ExtractionTask


@define
class CsvExtractionTask(ExtractionTask):
    _extraction_engine: CsvExtractionEngine = field(default=None, kw_only=True, alias="extraction_engine")

    @property
    def extraction_engine(self) -> CsvExtractionEngine:
        if self._extraction_engine is None:
            if self.structure is not None:
                self._extraction_engine = CsvExtractionEngine(prompt_driver=self.structure.config.prompt_driver)
            else:
                raise ValueError("Extraction Engine is not set.")
        return self._extraction_engine

    @extraction_engine.setter
    def extraction_engine(self, value: CsvExtractionEngine) -> None:
        self._extraction_engine = value
