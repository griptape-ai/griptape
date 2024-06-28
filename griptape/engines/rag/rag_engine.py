from typing import Optional
from attrs import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.stages import QueryRagStage, GenerationRagStage, RetrievalRagStage


@define(kw_only=True)
class RagEngine:
    query_stage: Optional[QueryRagStage] = field(default=None)
    retrieval_stage: Optional[RetrievalRagStage] = field(default=None)
    generation_stage: Optional[GenerationRagStage] = field(default=None)

    def __attrs_post_init__(self) -> None:
        modules = []

        if self.query_stage is not None:
            modules.extend(self.query_stage.modules)

        if self.retrieval_stage is not None:
            modules.extend(self.retrieval_stage.modules)

        if self.generation_stage is not None:
            modules.extend(self.generation_stage.modules)

        module_names = [m.name for m in modules]

        if len(module_names) > len(set(module_names)):
            raise ValueError("module names have to be unique")

    def process_query(self, query: str) -> RagContext:
        return self.process(RagContext(query=query))

    def process(self, context: RagContext) -> RagContext:
        if self.query_stage:
            context = self.query_stage.run(context)

        if self.retrieval_stage:
            context = self.retrieval_stage.run(context)

        if self.generation_stage:
            context = self.generation_stage.run(context)

        return context
