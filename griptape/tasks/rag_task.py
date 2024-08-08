from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.engines.rag import RagEngine


@define
class RagTask(BaseTextInputTask):
    _rag_engine: RagEngine = field(kw_only=True, default=None, alias="rag_engine")

    @property
    def rag_engine(self) -> RagEngine:
        if self._rag_engine is None:
            if self.structure is not None:
                self._rag_engine = self.structure.rag_engine
            else:
                raise ValueError("rag_engine is not set.")
        return self._rag_engine

    @rag_engine.setter
    def rag_engine(self, value: RagEngine) -> None:
        self._rag_engine = value

    def run(self) -> BaseArtifact:
        outputs = self.rag_engine.process_query(self.input.to_text()).outputs

        if len(outputs) > 0:
            return ListArtifact(outputs)
        else:
            return ErrorArtifact("empty output")
