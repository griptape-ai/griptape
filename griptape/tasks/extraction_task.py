from __future__ import annotations
from attrs import define, field
from griptape.tasks import BaseTextInputTask
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.engines import BaseExtractionEngine
    from griptape.artifacts import ListArtifact, ErrorArtifact


@define
class ExtractionTask(BaseTextInputTask):
    _extraction_engine: BaseExtractionEngine = field(kw_only=True, default=None, alias="extraction_engine")
    args: dict = field(kw_only=True)

    @property
    def extraction_engine(self) -> BaseExtractionEngine:
        return self._extraction_engine

    def run(self) -> ListArtifact | ErrorArtifact:
        return self.extraction_engine.extract(self.input.to_text(), rulesets=self.all_rulesets, **self.args)
