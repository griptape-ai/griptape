---
search:
  boost: 2 
---

## RAG Engines

!!! note
    This section is a work in progress.

`RagEngine` is an abstraction for implementing modular RAG pipelines.

`RagContext` is a container object for passing around RAG context. 

### RAG Stages
- `QueryRagStage` is for parsing and expanding queries.
- `RetrievalRagStage` is for retrieving content.
- `ResponseRagStage` is for augmenting and generating outputs.

### RAG Modules

#### Query

No modules implemented yet.

#### Retrieval
- `TextRetrievalRagModule` is for retrieving text chunks.
- `TextLoaderRetrievalRagModule` is for retrieving data with text loaders in real time.
- `TextChunksRerankRagModule` is for re-ranking retrieved results.

#### Response
- `MetadataBeforeResponseRagModule` is for appending metadata.
- `RulesetsBeforeResponseRagModule` is for appending rulesets.
- `PromptResponseRagModule` is for generating responses based on retrieved text chunks.
- `TextChunksResponseRagModule` is for responding with retrieved text chunks.
- `FootnotePromptResponseRagModule` is for responding with automatic footnotes from text chunk references.

### Example

```python
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptResponseRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifacts = [
    TextArtifact("Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."),
    TextArtifact("Griptape Agents provide incredible power and flexibility when working with large language models.")
]
vector_store.upsert_text_artifacts({"griptape": artifacts})

engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                vector_store_driver=vector_store,
                query_params={
                    "namespace": "griptape",
                    "top_n": 20
                }
            )
        ]
    ),
    response_stage=ResponseRagStage(
        response_module=PromptResponseRagModule(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
        )
    )
)

print(
    engine.process_query("what are Griptape agents?").output.to_text()
)
```
