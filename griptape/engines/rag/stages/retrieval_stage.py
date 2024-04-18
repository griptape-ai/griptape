import itertools
from concurrent import futures
from attr import define, field, Factory
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules.retrieval import BaseRetriever
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class RetrievalStage(BaseStage):
    text_retrievers: list[BaseRetriever] = field()
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()))

    def run(self, context: RagContext) -> RagContext:
        result = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context.query) for r in self.text_retrievers]
        )

        context.text_chunks = list(itertools.chain.from_iterable(result))

        return context
