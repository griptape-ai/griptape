import logging
from attr import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseGenerationModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class GenerationStage(BaseStage):
    generator_modules: list[BaseGenerationModule] = field()

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"GenerationStage: running {len(self.generator_modules)} generator modules sequentially")

        for generator in self.generator_modules:
            context = generator.run(context)

        return context
