from __future__ import annotations

from typing import Union

from attrs import Factory, define, field

from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.engines.rag import RagEngine
from griptape.tasks import BaseTextInputTask


@define
class RagTask(BaseTextInputTask[Union[ListArtifact, ErrorArtifact]]):
    rag_engine: RagEngine = field(kw_only=True, default=Factory(lambda: RagEngine()))

    def try_run(self) -> ListArtifact | ErrorArtifact:
        outputs = self.rag_engine.process_query(self.input.to_text()).outputs

        if len(outputs) > 0:
            return ListArtifact(outputs)
        return ErrorArtifact("empty output")
