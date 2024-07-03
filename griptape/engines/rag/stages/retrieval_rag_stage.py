import itertools
import logging
from typing import Optional
from attrs import define, field
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRerankRagModule, BaseRagModule
from griptape.engines.rag.modules import BaseRetrievalRagModule
from griptape.engines.rag.stages import BaseRagStage


@define(kw_only=True)
class RetrievalRagStage(BaseRagStage):
    retrieval_modules: list[BaseRetrievalRagModule] = field()
    rerank_module: Optional[BaseRerankRagModule] = field(default=None)
    max_chunks: Optional[int] = field(default=None)

    @property
    def modules(self) -> list[BaseRagModule]:
        ms = []

        ms.extend(self.retrieval_modules)

        if self.rerank_module is not None:
            ms.append(self.rerank_module)

        return ms

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"RetrievalStage: running {len(self.retrieval_modules)} retrieval modules in parallel")

        with self.futures_executor_fn() as executor:
            results = utils.execute_futures_list([executor.submit(r.run, context) for r in self.retrieval_modules])

        # flatten the list of lists
        results = list(itertools.chain.from_iterable(results))

        # deduplicate the list
        chunks_before_dedup = len(results)
        results = list({str(c.value): c for c in results}.values())
        chunks_after_dedup = len(results)

        logging.info(
            f"RetrievalStage: deduplicated {chunks_before_dedup - chunks_after_dedup} "
            f"chunks ({chunks_before_dedup} - {chunks_after_dedup})"
        )

        context.text_chunks = [a for a in results if isinstance(a, TextArtifact)]

        if self.rerank_module:
            logging.info(f"RetrievalStage: running rerank module on {chunks_after_dedup} chunks")

            context.text_chunks = [a for a in self.rerank_module.run(context) if isinstance(a, TextArtifact)]

        if self.max_chunks:
            context.text_chunks = context.text_chunks[: self.max_chunks]

        return context
