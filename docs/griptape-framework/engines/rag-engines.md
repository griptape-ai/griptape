---
search:
  boost: 2
---

## RAG Engines

[Rag Engine](../../reference/griptape/engines/rag/index.md) is an abstraction for implementing modular retrieval augmented generation (RAG) pipelines.

### RAG Stages

`RagEngine`s consist of three _stages_: `QueryRagStage`, `RetrievalRagStage`, and `ResponseRagStage`. These stages are always executed sequentially. Each stage comprises multiple _modules_, which are executed in a customized manner. Due to this unique structure, `RagEngines` are not intended to replace [Workflows](../structures/workflows.md) or [Pipelines](../structures/pipelines.md).

### RAG Modules

RAG modules are used to implement actions in the different stages of the RAG pipeline. `RagEngine` enables developers to easily add new modules to experiment with novel RAG strategies.

The three stages of the pipeline implemented in RAG Engines, together with their purposes and associated modules, are as follows:

### Query Stage

This stage is used for modifying input queries before they are submitted.

#### Query Stage Modules

- `TranslateQueryRagModule` is for translating the query into another language.

### Retrieval Stage

Results are retrieved in this stage, either from a vector store in the form of chunks, or with a text loader. You may optionally use a rerank module in this stage to rerank results in order of their relevance to the original query.

#### Retrieval Stage Modules

- `TextChunksRerankRagModule` is for re-ranking retrieved results.
- `TextLoaderRetrievalRagModule` is for retrieving data with text loaders in real time.
- `VectorStoreRetrievalRagModule` is for retrieving text chunks from a vector store.

### Response Stage

Responses are generated in this final stage.

#### Response Stage Modules

- `PromptResponseRagModule` is for generating responses based on retrieved text chunks.
- `TextChunksResponseRagModule` is for responding with retrieved text chunks.
- `FootnotePromptResponseRagModule` is for responding with automatic footnotes from text chunk references.

### RAG Context

`RagContext` is a container object for passing around queries, text chunks, module configs, and other metadata. `RagContext` is modified by modules when appropriate. Some modules support runtime config overrides through `RagContext.module_configs`.

### Simple Example

The following example shows a simple RAG pipeline that retrieves data from a local vector store and generates a response:

```python
--8<-- "docs/griptape-framework/engines/src/rag_engines_simple.py"
```

### Advanced Example

The following example shows an advanced RAG pipeline that does the following:

- Translates incoming queries into English.
- Retrieves data from a local vector store and a local file.
- Reranks the results using the local rerank driver.
- Generates multiple types of response.

```python
--8<-- "docs/griptape-framework/engines/src/rag_engines_advanced.py"
```

### RAG Tool

See [RagTool](../tools/official-tools/index.md#rag) for an example of how to integrate the RAG Tool with an Agent.
