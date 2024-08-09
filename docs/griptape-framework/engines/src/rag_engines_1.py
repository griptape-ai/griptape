from griptape.artifacts import ErrorArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, TranslateQueryRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import QueryRagStage, ResponseRagStage, RetrievalRagStage
from griptape.loaders import WebLoader

prompt_driver = OpenAiChatPromptDriver(model="gpt-4o", temperature=0)

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifacts = WebLoader(max_tokens=500).load("https://www.griptape.ai")
if isinstance(artifacts, ErrorArtifact):
    raise ValueError(artifacts.value)

vector_store.upsert_text_artifacts({"griptape": artifacts})

rag_engine = RagEngine(
    query_stage=QueryRagStage(query_modules=[TranslateQueryRagModule(prompt_driver=prompt_driver, language="English")]),
    retrieval_stage=RetrievalRagStage(
        max_chunks=5,
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                name="MyAwesomeRetriever", vector_store_driver=vector_store, query_params={"top_n": 20}
            )
        ],
    ),
    response_stage=ResponseRagStage(response_module=PromptResponseRagModule(prompt_driver=prompt_driver)),
)

rag_context = RagContext(
    query="¿Qué ofrecen los servicios en la nube de Griptape?",
    module_configs={"MyAwesomeRetriever": {"query_params": {"namespace": "griptape"}}},
)

print(rag_engine.process(rag_context).output.to_text())
