from __future__ import annotations

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact
from griptape.engines.rag import RagEngine
from griptape.tasks import BaseTextInputTask


@define
class RagTask(BaseTextInputTask):
    rag_engine: RagEngine = field(kw_only=True, default=Factory(lambda: RagEngine()))

    def try_run(self) -> BaseArtifact:
        outputs = self.rag_engine.process_query(self.input.to_text()).outputs

        if len(outputs) > 0:
            return ListArtifact(outputs)
        else:
            return ErrorArtifact("empty output")
