from __future__ import annotations

import itertools
import logging
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.engines.rag.stages import BaseRagStage

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext
    from griptape.engines.rag.modules import BaseRagModule, BaseRerankRagModule, BaseRetrievalRagModule


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
        logging.info("RetrievalStage: running %s retrieval modules in parallel", len(self.retrieval_modules))

        with self.futures_executor_fn() as executor:
            results = utils.execute_futures_list([executor.submit(r.run, context) for r in self.retrieval_modules])

        # flatten the list of lists
        results = list(itertools.chain.from_iterable(results))

        # deduplicate the list
        chunks_before_dedup = len(results)
        results = list({str(c.value): c for c in results}.values())
        chunks_after_dedup = len(results)

        logging.info(
            "RetrievalStage: deduplicated %s " "chunks (%s - %s)",
            chunks_before_dedup - chunks_after_dedup,
            chunks_before_dedup,
            chunks_after_dedup,
        )

        context.text_chunks = [a for a in results if isinstance(a, TextArtifact)]

        if self.rerank_module:
            logging.info("RetrievalStage: running rerank module on %s chunks", chunks_after_dedup)

            context.text_chunks = [a for a in self.rerank_module.run(context) if isinstance(a, TextArtifact)]

        if self.max_chunks:
            context.text_chunks = context.text_chunks[: self.max_chunks]

        return context
