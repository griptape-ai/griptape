from attrs import define, field
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagEngine
from griptape.tasks import BaseTextInputTask


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

    def run(self) -> TextArtifact:
        return self.rag_engine.process_query(self.input.to_text()).output
