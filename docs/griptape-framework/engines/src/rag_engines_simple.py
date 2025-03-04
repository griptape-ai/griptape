from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import (
    ResponseRagStage,
    RetrievalRagStage,
)
from griptape.loaders import WebLoader

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

# Load some data from a couple sources.
web_artifact = WebLoader().load("https://griptape.ai")
chunks = TextChunker(max_tokens=250).chunk(web_artifact)
vector_store.upsert_collection({"griptape": chunks})

rag_engine = RagEngine(
    # This stage is responsible for retrieving the relevant chunks.
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                name="WebRetriever",
                vector_store_driver=vector_store,
                query_params={"namespace": "griptape"},
            ),
        ],
    ),
    # This stage is responsible for generating the final response.
    response_stage=ResponseRagStage(
        response_modules=[
            PromptResponseRagModule(),
        ]
    ),
)

rag_context = RagContext(query="What is Griptape?")
rag_context = rag_engine.process(rag_context)
print(rag_context.outputs[0].to_text())
