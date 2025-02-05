# What are Data Sources?

Data Sources allow you to bring your own data to Griptape Cloud. By pointing Griptape Cloud at your data, you can make it accessible to your LLM-powered applications.

Data Sources are the first step to Griptape's retrieval-augemented generaton (RAG) pipeline. They allow you to bring your own data to ingest and transform. You can then make one or more Data Source available to your AI applications via [Knowledge Bases](../knowledge-bases/create-knowledge-base.md)

Connecting to external data -- by creating a Data Source -- is the first step of building a retrieval-augmented AI application. Once you create a Data Source, you can make it available to your application by adding it to a knowledge base.

Griptape Data Sources extract, ingest, and prepare your data so that it can be retrieved and used by LLMs. This is an important step because LLMs work best with data when it is represented in a particular format. These formats often differ from how the information might best be presented to human users or even other software applications. For example, the text of a web page must be cleaned to remove extraneous information, annotated with metadata, segmented into chunks, and converted into vector embeddings before it can be stored in a suitable database.

Typically, developers must deploy and operate this process themselves. It can be time consuming, error-prone, and costly. In Griptape Cloud, this process is automated for you.
