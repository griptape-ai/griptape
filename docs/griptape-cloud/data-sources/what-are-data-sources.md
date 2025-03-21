# What are Data Sources?

All AI-powered software applications require data to perform their jobs. A significant amount of information is encoded into Large language models (LLMs) during training, so a basic applications may not need anything other than a user's input 'prompt' to generate useful output.

Data Sources in Griptape Cloud allow you to bring your own data and use this in your AI applications. Creating a Griptape Cloud Data source makes your data accessible to your LLM-powered applications running on Griptape Cloud.

Data Sources are the first step in creating a Griptape Cloud retrieval-augemented generation (RAG) pipeline, or [Retriever](../retrievers/what-are-retrievers.md). Data Sources allow you to ingest your own data, and optionally to transform it. You can then make one or more Data Sources available to your AI applications either via a [Knowledge Base](../knowledge-bases/create-knowledge-base.md) or a [Retriever](../retrievers/what-are-retrievers.md).

Griptape Cloud Data Sources extract, ingest, and prepare your data so that it can be retrieved and used by LLMs. This is an important step because LLMs work best with data when it is represented in a specific formats. These formats often differ from how the information might best be presented to human users or even other software applications. For example, the contents of a web page must be cleaned to remove extraneous information such as HTML markup tags leaving only the text, then segmented into chunks, and converted into vector embeddings before it can be stored in a suitable database.

Outside Griptape Cloud, you have to write code to implement these data preparation steps, and operate this process themselves. This can be time consuming, error-prone, and costly. With Griptape Cloud, this process is automated for you.
