## RAG Engines

!!! note
    This section is a work in progress.

`RagEngine` is an abstraction for implementing modular RAG pipelines.

`RagContext` is a container object for passing around RAG context. 

### RAG Stages
- `QueryRagStage` is for parsing and expanding queries.
- `RetrievalRagStage` is for retrieving content.
- `GenerationRagStage` is for augmenting and generating outputs.

### RAG Modules

#### Query
- `RelatedQueryGenerationRagModule` is for generating related queries.

#### Retrieval
- `TextRetrievalRagModule` is for retrieving text chunks.
- `TextRerankRagModule` is for re-ranking retrieved results.

#### Generation
- `MetadataGenerationRagModule` is for appending metadata.
- `RulesetsGenerationRagModule` is for appending rulesets.
- `PromptGenerationRagModule` is for generating responses based on retrieved text chunks.

### Example

```python
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import TextRetrievalRagModule, PromptGenerationRagModule
from griptape.engines.rag.stages import RetrievalRagStage, GenerationRagStage

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifacts = [
    TextArtifact("Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."),
    TextArtifact("Griptape Agents provide incredible power and flexibility when working with large language models.")
]
vector_store.upsert_text_artifacts({"griptape": artifacts})

engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            TextRetrievalRagModule(
                namespace="griptape",
                vector_store_driver=vector_store,
                top_n=20
            )
        ]
    ),
    generation_stage=GenerationRagStage(
        generation_module=PromptGenerationRagModule(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
        )
    )
)

print(
    engine.process_query("what are Griptape agents?").output.to_text()
)
```