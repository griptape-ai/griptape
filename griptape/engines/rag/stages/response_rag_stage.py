from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.engines.rag.stages import BaseRagStage

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext
    from griptape.engines.rag.modules import (
        BaseAfterResponseRagModule,
        BaseBeforeResponseRagModule,
        BaseRagModule,
        BaseResponseRagModule,
    )


@define(kw_only=True)
class ResponseRagStage(BaseRagStage):
    before_response_modules: list[BaseBeforeResponseRagModule] = field(factory=list)
    response_module: BaseResponseRagModule = field()
    after_response_modules: list[BaseAfterResponseRagModule] = field(factory=list)

    @property
    def modules(self) -> list[BaseRagModule]:
        ms = []

        ms.extend(self.before_response_modules)
        ms.extend(self.after_response_modules)

        if self.response_module is not None:
            ms.append(self.response_module)

        return ms

    def run(self, context: RagContext) -> RagContext:
        logging.info("GenerationStage: running %s before modules sequentially", len(self.before_response_modules))

        for generator in self.before_response_modules:
            context = generator.run(context)

        logging.info("GenerationStage: running generation module")

        context = self.response_module.run(context)

        logging.info("GenerationStage: running %s after modules sequentially", len(self.after_response_modules))

        for generator in self.after_response_modules:
            context = generator.run(context)

        return context
