# Types of Knowledge Base

Griptape Cloud supports two different types of Knowledge Base:

## Vector Knowledge Bases

Vector Knowledge Bases generate embeddings from the data in the specified data source or data sources and upsert this, together with the original data, into a database that acts as a vector store. Griptape Cloud has a built-in fully-managed vector store. You can also provide your own Postgres & pgvector endpoint and configure Griptape Cloud to use this as the vector store for your Knowledge Base.

Queries made against Vector Knowledge Bases are vector search queries.

## Hybrid Knowledge Bases

Hybrid Knowledge Bases also generate embeddings for unstructured data. They differ from Vector Knowledge Bases in that they are also able to store structured data alongside vectors and unstructured data. Hybrid Knowledge Bases are accessed via a Tool within Griptape Cloud that supports hybrid queries combining structured and unstructured data.

Griptape Cloud currently supports the creation of Hybrid Knowledge Bases from CSV data (via the Amazon S3, Google Drive & Griptape Cloud Data Lake Data Source types), and from Google Sheets through the Google Drive Data Source type.

Queries made against Hybrid Knowledge Bases can be SQL queries made against structured fields, vector search queries made against unstructured fields, or a combination of the two query types.
