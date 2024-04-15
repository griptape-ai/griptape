from attr import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.stages import QueryStage, GenerationStage, RetrievalStage


@define(kw_only=True)
class RagEngine:
    query_stage: QueryStage = field()
    retrieval_stage: RetrievalStage = field()
    generation_stage: GenerationStage = field()

    def process_query(self, query: str) -> RagContext:
        return self.process(
            RagContext(
                query=query
            )
        )

    def process(self, context: RagContext) -> RagContext:
        context = self.query_stage.run(context)
        context = self.retrieval_stage.run(context)
        context = self.generation_stage.run(context)

        return context
