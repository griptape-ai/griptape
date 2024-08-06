from __future__ import annotations

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.engines.rag import RagEngine
from griptape.tasks import BaseTextInputTask


@define
class RagTask(BaseTextInputTask):
    rag_engine: RagEngine = field(kw_only=True, default=Factory(lambda: RagEngine()))

    def run(self) -> BaseArtifact:
        result = self.rag_engine.process_query(self.input.to_text()).output

        if result is None:
            return ErrorArtifact("empty output")
        else:
            return result
