from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import ListArtifact
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.engines import BaseExtractionEngine


@define
class ExtractionTask(BaseTextInputTask[ListArtifact]):
    extraction_engine: BaseExtractionEngine = field(kw_only=True)
    args: dict = field(kw_only=True, factory=dict)

    def try_run(self) -> ListArtifact:
        return self.extraction_engine.extract_artifacts(ListArtifact([self.input]), rulesets=self.rulesets, **self.args)
