import logging
from attrs import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseQueryRagModule, BaseRagModule
from griptape.engines.rag.stages import BaseRagStage


@define(kw_only=True)
class QueryRagStage(BaseRagStage):
    query_modules: list[BaseQueryRagModule] = field()

    @property
    def modules(self) -> list[BaseRagModule]:
        return self.query_modules  # pyright: ignore

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"QueryStage: running {len(self.query_modules)} query generation modules in parallel")

        with self.futures_executor_fn() as executor:
            utils.execute_futures_list([executor.submit(r.run, context) for r in self.query_modules])

        return context
