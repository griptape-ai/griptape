from attr import define, field, Factory
from typing import Optional
from griptape.artifacts import TextArtifact
from griptape.engines import BaseQueryEngine, VectorQueryEngine
from griptape.loaders import TextLoader
from griptape.tasks import BaseTextInputTask


@define
class TextQueryTask(BaseTextInputTask):
    _query_engine: BaseQueryEngine = field(kw_only=True, default=None, alias="query_engine")
    loader: TextLoader = field(default=Factory(lambda: TextLoader()), kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)
    top_n: Optional[int] = field(default=None, kw_only=True)

    @property
    def query_engine(self) -> BaseQueryEngine:
        if self._query_engine is None:
            if self.structure is not None:
                self._query_engine = VectorQueryEngine(
                    prompt_driver=self.structure.config.global_drivers.prompt_driver,
                    vector_store_driver=self.structure.config.global_drivers.vector_store_driver,
                )
            else:
                raise ValueError("Query Engine is not set.")
        return self._query_engine

    @query_engine.setter
    def query_engine(self, value: BaseQueryEngine) -> None:
        self._query_engine = value

    def run(self) -> TextArtifact:
        return self.query_engine.query(
            self.input.to_text(), namespace=self.namespace, rulesets=self.all_rulesets, top_n=self.top_n
        )
