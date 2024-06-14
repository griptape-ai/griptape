import itertools
import logging
from typing import Optional
from attrs import define, field
from griptape import utils
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRerankModule
from griptape.engines.rag.modules.retrieval import BaseRetrievalModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class RetrievalStage(BaseStage):
    retrieval_modules: list[BaseRetrievalModule] = field()
    rerank_module: Optional[BaseRerankModule] = field(default=None)
    max_chunks: Optional[int] = field(default=None)

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"RetrievalStage: running {len(self.retrieval_modules)} retrieval modules in parallel")

        results = utils.execute_futures_list(
            [self.futures_executor.submit(r.run, context) for r in self.retrieval_modules]
        )

        # flatten the list of lists
        context.text_chunks = list(itertools.chain.from_iterable(results))

        # deduplicate the list
        chunks_before_dedup = len(context.text_chunks)
        context.text_chunks = list({str(c.value): c for c in context.text_chunks}.values())
        chunks_after_dedup = len(context.text_chunks)

        logging.info(
            f"RetrievalStage: deduplicated {chunks_before_dedup - chunks_after_dedup} "
            f"chunks ({chunks_before_dedup} - {chunks_after_dedup})"
        )

        if self.rerank_module:
            logging.info(f"RetrievalStage: running rerank module on {chunks_after_dedup} chunks")

            context.text_chunks = self.rerank_module.run(context)

        if self.max_chunks:
            context.text_chunks = context.text_chunks[0 : self.max_chunks]

        return context
