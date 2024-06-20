import itertools
import logging
from attrs import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseQueryRagModule
from griptape.engines.rag.stages import BaseRagStage


@define(kw_only=True)
class QueryRagStage(BaseRagStage):
    query_generation_modules: list[BaseQueryRagModule] = field()

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"QueryStage: running {len(self.query_generation_modules)} query generation modules in parallel")

        results = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.query_generation_modules]
        )

        context.alternative_queries = list(itertools.chain.from_iterable(results))

        return context
