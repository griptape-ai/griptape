import itertools
from attr import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules.retrieval import BaseRetrievalModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class RetrievalStage(BaseStage):
    retrieval_modules: list[BaseRetrievalModule] = field()

    def run(self, context: RagContext) -> RagContext:
        result = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.retrieval_modules]
        )

        context.text_chunks = list(itertools.chain.from_iterable(result))

        return context
