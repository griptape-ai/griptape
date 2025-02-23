from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.rerank.local import LocalRerankDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    TextChunksRerankRagModule,
    TranslateQueryRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import (
    QueryRagStage,
    ResponseRagStage,
    RetrievalRagStage,
)
from griptape.loaders import WebLoader
from griptape.rules import Rule, Ruleset

prompt_driver = OpenAiChatPromptDriver(model="gpt-4o", temperature=0)

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())
artifact = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker(max_tokens=500).chunk(artifact)

vector_store.upsert_text_artifacts(
    {
        "griptape": chunks,
    }
)

rag_engine = RagEngine(
    query_stage=QueryRagStage(query_modules=[TranslateQueryRagModule(prompt_driver=prompt_driver, language="english")]),
    retrieval_stage=RetrievalRagStage(
        max_chunks=5,
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                name="MyAwesomeRetriever",
                vector_store_driver=vector_store,
                query_params={"top_n": 20},
            )
        ],
        rerank_module=TextChunksRerankRagModule(rerank_driver=LocalRerankDriver()),
    ),
    response_stage=ResponseRagStage(
        response_modules=[
            PromptResponseRagModule(
                prompt_driver=prompt_driver,
                rulesets=[Ruleset(name="persona", rules=[Rule("Talk like a pirate")])],
            )
        ]
    ),
)

rag_context = RagContext(
    query="¿Qué ofrecen los servicios en la nube de Griptape?",
    module_configs={"MyAwesomeRetriever": {"query_params": {"namespace": "griptape"}}},
)

print(rag_engine.process(rag_context).outputs[0].to_text())
