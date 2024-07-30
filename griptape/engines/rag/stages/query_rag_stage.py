from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import define, field

from griptape import utils
from griptape.engines.rag.stages import BaseRagStage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.engines.rag import RagContext
    from griptape.engines.rag.modules import BaseQueryRagModule, BaseRagModule


@define(kw_only=True)
class QueryRagStage(BaseRagStage):
    query_modules: list[BaseQueryRagModule] = field()

    @property
    def modules(self) -> Sequence[BaseRagModule]:
        return self.query_modules

    def run(self, context: RagContext) -> RagContext:
        logging.info("QueryStage: running %s query generation modules in parallel", len(self.query_modules))

        with self.futures_executor_fn() as executor:
            utils.execute_futures_list([executor.submit(r.run, context) for r in self.query_modules])

        return context
