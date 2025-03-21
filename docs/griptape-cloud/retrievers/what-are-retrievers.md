# What are Retrievers?

Retrievers provide retrieval augmented generation capabilities within Griptape Cloud. They are a fully-managed implementation of the [RAG Engine](../../griptape-framework/engines/rag-engines.md) within the [Griptape Framework](../../griptape-framework/index.md).

Using a Retriever will give more accurate and effective results than using a Knowledge Base because Retrievers provide reranking capabilities.

Retrievers include a standard set of modules known as Retreiver Components (to avoid confusion with the RAG modules in Griptape Framework). Retreiver Components are used to implement the different stages of the RAG pipeline.

## Response Component Configuration

If you are using your Retriever with a Griptape Cloud Assistant, set the *Response* *Type* to *Text Chunks*. If your use-case requires a natural language response, set the *Response* *Type* to *Prompt with Rulesets* and specify which *Rulesets* you wish to apply.
