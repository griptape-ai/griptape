from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import define, field

from griptape import utils
from griptape.engines.rag.stages import BaseRagStage
from griptape.utils import with_contextvars

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext
    from griptape.engines.rag.modules import (
        BaseRagModule,
        BaseResponseRagModule,
    )


@define(kw_only=True)
class ResponseRagStage(BaseRagStage):
    response_modules: list[BaseResponseRagModule] = field()

    @property
    def modules(self) -> list[BaseRagModule]:
        ms = []

        ms.extend(self.response_modules)

        return ms

    def run(self, context: RagContext) -> RagContext:
        logging.info("ResponseRagStage: running %s retrieval modules in parallel", len(self.response_modules))

        with self.create_futures_executor() as futures_executor:
            results = utils.execute_futures_list(
                [futures_executor.submit(with_contextvars(r.run), context) for r in self.response_modules]
            )

        context.outputs = results

        return context
