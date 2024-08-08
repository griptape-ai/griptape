from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifacts = [
    TextArtifact("Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."),
    TextArtifact("Griptape Agents provide incredible power and flexibility when working with large language models."),
]
vector_store.upsert_text_artifacts({"griptape": artifacts})

engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                vector_store_driver=vector_store, query_params={"namespace": "griptape", "top_n": 20}
            )
        ]
    ),
    response_stage=ResponseRagStage(
        response_module=PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))
    ),
)

print(engine.process_query("what are Griptape agents?").output.to_text())
