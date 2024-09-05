---
search:
  boost: 2 
---

## RAG Engines

!!! note
    This section is a work in progress.

[Rag Engine](../../reference/griptape/engines/rag/index.md) is an abstraction for implementing modular retrieval augmented generation (RAG) pipelines.

### RAG Stages

`RagEngine`s consist of three _stages_: `QueryRagStage`, `RetrievalRagStage`, and `ResponseRagStage`. These stages are always executed sequentially. Each stage comprises multiple _modules_, which are executed in a customized manner. Due to this unique structure, `RagEngines` are not intended to replace [Workflows](../structures/workflows.md) or [Pipelines](../structures/pipelines.md).


- `QueryRagStage` is used for modifying user queries.
- `RetrievalRagStage` is used for retrieving and re-ranking text chunks.
- `ResponseRagStage` is used for generating responses.

### RAG Modules

RAG modules are used to implement concrete actions in the RAG pipeline. `RagEngine` enables developers to easily add new modules to experiment with novel RAG strategies.

#### Query Modules

- `TranslateQueryRagModule` is for translating the query into another language.

#### Retrieval/Rerank Modules
- `TextChunksRerankRagModule` is for re-ranking retrieved results.
- `TextLoaderRetrievalRagModule` is for retrieving data with text loaders in real time.
- `VectorStoreRetrievalRagModule` is for retrieving text chunks from a vector store.

#### Response Modules
- `PromptResponseRagModule` is for generating responses based on retrieved text chunks.
- `TextChunksResponseRagModule` is for responding with retrieved text chunks.
- `FootnotePromptResponseRagModule` is for responding with automatic footnotes from text chunk references.

### RAG Context

`RagContext` is a container object for passing around queries, text chunks, module configs, and other metadata. `RagContext` is modified by modules when appropriate. Some modules support runtime config overrides through `RagContext.module_configs`.

### Example

The following example shows a simple RAG pipeline that translates incoming queries into English, retrieves data from a local vector store, and generates a response:

```python
--8<-- "docs/griptape-framework/engines/src/rag_engines_1.py"
```
