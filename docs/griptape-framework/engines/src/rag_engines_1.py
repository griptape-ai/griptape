from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine, RagContext
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptResponseRagModule, TranslateQueryRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage, QueryRagStage
from griptape.loaders import WebLoader
from griptape.rules import Ruleset, Rule

prompt_driver = OpenAiChatPromptDriver(model="gpt-4o", temperature=0)

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

vector_store.upsert_text_artifacts(
    {
        "griptape": WebLoader(max_tokens=500).load("https://www.griptape.ai"),
    }
)

rag_engine = RagEngine(
    query_stage=QueryRagStage(query_modules=[TranslateQueryRagModule(prompt_driver=prompt_driver, language="english")]),
    retrieval_stage=RetrievalRagStage(
        max_chunks=5,
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                name="MyAwesomeRetriever", vector_store_driver=vector_store, query_params={"top_n": 20}
            )
        ],
    ),
    response_stage=ResponseRagStage(
        response_modules=[
            PromptResponseRagModule(
                prompt_driver=prompt_driver, rulesets=[Ruleset(name="persona", rules=[Rule("Talk like a pirate")])]
            )
        ]
    ),
)

rag_context = RagContext(
    query="¿Qué ofrecen los servicios en la nube de Griptape?",
    module_configs={"MyAwesomeRetriever": {"query_params": {"namespace": "griptape"}}},
)

print(rag_engine.process(rag_context).outputs[0].to_text())
