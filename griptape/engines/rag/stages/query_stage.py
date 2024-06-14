import itertools
import logging
from attrs import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseQueryModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class QueryStage(BaseStage):
    query_generation_modules: list[BaseQueryModule] = field()

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"QueryStage: running {len(self.query_generation_modules)} query generation modules in parallel")

        results = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.query_generation_modules]
        )

        context.alternative_queries = list(itertools.chain.from_iterable(results))

        return context
