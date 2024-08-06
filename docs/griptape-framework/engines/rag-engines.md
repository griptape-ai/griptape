---
search:
  boost: 2 
---

## RAG Engines

!!! note
    This section is a work in progress.

[Rag Engine](../../reference/griptape/engines/rag/index.md) is an abstraction for implementing modular retrieval augmented generation (RAG) pipelines.

### RAG Stages

`RagEngine`s consist of three stages: `QueryRagStage`, `RetrievalRagStage`, and `ResponseRagStage`. Stages are always executed sequentially. `RagEngine`s are not meant to replace [Workflows](../../reference/griptape/structures/workflows.md); that's why they don't implement arbitrary DAGs.

- `QueryRagStage` is used for modifying user queries.
- `RetrievalRagStage` is used for retrieving and re-ranking text chunks.
- `ResponseRagStage` is used for generating responses.

### RAG Modules

RAG modules are used to implement concrete actions in the RAG pipeline. `RagEngine` enables developers to easily add new modules to experiment with novel RAG strategies.

#### Query Modules

- `TranslateQueryRagModule` is for translating the query into another language.

#### Retrieval Modules
- `TextRetrievalRagModule` is for retrieving text chunks.
- `TextLoaderRetrievalRagModule` is for retrieving data with text loaders in real time.
- `TextChunksRerankRagModule` is for re-ranking retrieved results.

#### Response Modules
- `MetadataBeforeResponseRagModule` is for appending metadata.
- `RulesetsBeforeResponseRagModule` is for appending rulesets.
- `PromptResponseRagModule` is for generating responses based on retrieved text chunks.
- `TextChunksResponseRagModule` is for responding with retrieved text chunks.
- `FootnotePromptResponseRagModule` is for responding with automatic footnotes from text chunk references.

### RAG Context

`RagContext` is a container object for passing around queries, text chunks, module configs, and other metadata. `RagContext` is modified by modules when appropriate. Some modules support runtime config overrides through `RagContext.module_configs`.

### Example

The following example shows a simple RAG pipeline that translates incoming queries into English, retrieves data from a local vector store, and generates a response:

```python
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine, RagContext
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptResponseRagModule, TranslateQueryRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage, QueryRagStage
from griptape.loaders import WebLoader

prompt_driver = OpenAiChatPromptDriver(model="gpt-4o", temperature=0)

vector_store = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver()
)

vector_store.upsert_text_artifacts({
    "griptape": WebLoader(max_tokens=500).load("https://www.griptape.ai"),
})

rag_engine = RagEngine(
    query_stage=QueryRagStage(
        query_modules=[
            TranslateQueryRagModule(
                prompt_driver=prompt_driver,
                language="English"
            )
        ]
    ),
    retrieval_stage=RetrievalRagStage(
        max_chunks=5,
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                name="MyAwesomeRetriever",
                vector_store_driver=vector_store,
                query_params={
                    "top_n": 20
                }
            )
        ]
    ),
    response_stage=ResponseRagStage(
        response_module=PromptResponseRagModule(
            prompt_driver=prompt_driver
        )
    )
)

rag_context = RagContext(
    query="¿Qué ofrecen los servicios en la nube de Griptape?",
    module_configs={
        "MyAwesomeRetriever": {
            "query_params": {
                "namespace": "griptape"
            }
        }
    }
)

print(
    rag_engine.process(rag_context).output.to_text()
)
```