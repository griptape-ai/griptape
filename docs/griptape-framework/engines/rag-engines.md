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
--8<-- "griptape-framework/engines/src/rag_engines_1.py"
```
