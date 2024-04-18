import itertools
from attr import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseQueryModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class QueryStage(BaseStage):
    query_modules: list[BaseQueryModule] = field()

    def run(self, context: RagContext) -> RagContext:
        result = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.query_modules]
        )

        context.expanded_queries = list(itertools.chain.from_iterable(result))

        return context
