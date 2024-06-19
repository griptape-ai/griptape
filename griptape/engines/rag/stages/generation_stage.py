import logging
from attrs import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseGenerationRagModule, BaseBeforeGenerationRagModule, BaseAfterGenerationRagModule
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class GenerationStage(BaseStage):
    before_generator_modules: list[BaseBeforeGenerationRagModule] = field(factory=list)
    generation_module: BaseGenerationRagModule = field()
    after_generator_modules: list[BaseAfterGenerationRagModule] = field(factory=list)

    def run(self, context: RagContext) -> RagContext:
        logging.info(f"GenerationStage: running {len(self.before_generator_modules)} before modules sequentially")

        for generator in self.before_generator_modules:
            context = generator.run(context)

        logging.info("GenerationStage: running generation module")

        context = self.generation_module.run(context)

        logging.info(f"GenerationStage: running {len(self.after_generator_modules)} after modules sequentially")

        for generator in self.after_generator_modules:
            context = generator.run(context)

        return context
