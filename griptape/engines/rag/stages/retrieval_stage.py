import itertools
import logging
from typing import Optional
from attr import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRerankModule
from griptape.engines.rag.modules.retrieval import BaseRetrievalModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class RetrievalStage(BaseStage):
    retrieval_modules: list[BaseRetrievalModule] = field()
    rerank_module: Optional[BaseRerankModule] = field(default=None)

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"RetrievalStage: running {len(self.retrieval_modules)} retrieval modules in parallel")

        futures_results = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.retrieval_modules]
        )

        context.text_chunks = list(itertools.chain.from_iterable(futures_results))

        if self.rerank_module:
            logging.info(f"RetrievalStage: running rerank module")

            context.text_chunks = self.rerank_module.run(context)

        return context
