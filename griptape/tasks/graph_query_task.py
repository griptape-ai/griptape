from __future__ import annotations
from attr import define, field
from typing import Optional, TYPE_CHECKING
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.engines import GraphQueryEngine


@define
class GraphQueryTask(BaseTextInputTask):
    query_engine: GraphQueryEngine = field(kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    def run(self) -> TextArtifact:
        return self.query_engine.query(self.input.to_text(), namespace=self.namespace, rulesets=self.all_rulesets)
