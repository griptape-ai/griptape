from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import ErrorArtifact, ListArtifact
    from griptape.engines import BaseExtractionEngine


@define
class ExtractionTask(BaseTextInputTask):
    _extraction_engine: BaseExtractionEngine = field(kw_only=True, default=None, alias="extraction_engine")
    args: dict = field(kw_only=True)

    @property
    def extraction_engine(self) -> BaseExtractionEngine:
        return self._extraction_engine

    def run(self) -> ListArtifact | ErrorArtifact:
        return self.extraction_engine.extract(self.input.to_text(), rulesets=self.all_rulesets, **self.args)
