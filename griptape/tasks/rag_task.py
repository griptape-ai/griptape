from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import TextRetrievalModule, PromptGenerationModule, RulesetsGenerationModule
from griptape.engines.rag.stages import RetrievalStage, GenerationStage
from griptape.loaders import TextLoader
from griptape.tasks import BaseTextInputTask


@define
class RagTask(BaseTextInputTask):
    _rag_engine: RagEngine = field(kw_only=True, default=None, alias="rag_engine")
    loader: TextLoader = field(default=Factory(lambda: TextLoader()), kw_only=True)

    @property
    def rag_engine(self) -> RagEngine:
        if self._rag_engine is None:
            if self.structure is not None:
                self._rag_engine = RagEngine(
                    retrieval_stage=RetrievalStage(
                        retrieval_modules=[
                            TextRetrievalModule(
                                vector_store_driver=self.structure.config.global_drivers.vector_store_driver
                            )
                        ]
                    ),
                    generation_stage=GenerationStage(
                        before_generator_modules=[
                            RulesetsGenerationModule(
                                rulesets=self.all_rulesets
                            )
                        ],
                        generation_module=PromptGenerationModule(
                            prompt_driver=self.structure.config.global_drivers.prompt_driver,
                        )
                    ),
                )
            else:
                raise ValueError("rag_engine is not set.")
        return self._rag_engine

    @rag_engine.setter
    def rag_engine(self, value: RagEngine) -> None:
        self._rag_engine = value

    def run(self) -> TextArtifact:
        return self.rag_engine.process_query(self.input.to_text()).output
