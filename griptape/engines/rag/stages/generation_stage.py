from attr import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseGenerator
from griptape.engines.rag.stages import BaseStage


@define(kw_only=True)
class GenerationStage(BaseStage):
    generators: list[BaseGenerator] = field()

    def run(self, context: RagContext) -> RagContext:
        for generator in self.generators:
            context = generator.generate(context)

        return context
