from attr import define, field
from typing import Optional
from griptape.artifacts import TextArtifact
from griptape.engines import BaseQueryEngine
from griptape.tasks import BaseTextInputTask


@define
class TextQueryTask(BaseTextInputTask):
    query_engine: BaseQueryEngine = field(kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    def run(self) -> TextArtifact:
        return self.query_engine.query(self.input.to_text(), namespace=self.namespace, rulesets=self.all_rulesets)
