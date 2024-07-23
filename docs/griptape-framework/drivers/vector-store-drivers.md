---
search:
  boost: 2 
---

## Overview

Griptape provides a way to build drivers for vector DBs where embeddings can be stored and queried. Every Vector Store Driver implements the following methods:

- `upsert_text_artifact()` for updating or inserting a new [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) into vector DBs. The method will automatically generate embeddings for a given value.
- `upsert_text_artifacts()` for updating or inserting multiple [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s into vector DBs. The method will automatically generate embeddings for given values.
- `upsert_text()` for updating and inserting new arbitrary strings into vector DBs. The method will automatically generate embeddings for a given value.
- `upsert_vector()` for updating and inserting new vectors directly.
- `query()` for querying vector DBs.

Each Vector Store Driver takes a [BaseEmbeddingDriver](../../reference/griptape/drivers/embedding/base_embedding_driver.md) used to dynamically generate embeddings for strings.

!!! info
    When working with vector database indexes with Griptape Drivers, make sure the number of dimensions is equal to 1536. Nearly all embedding models create vectors with this number of dimensions. Check the documentation for your vector database on how to create/update vector indexes.

!!! info
    More Vector Store Drivers are coming soon.

## Vector Store Drivers

### Local

The [LocalVectorStoreDriver](../../reference/griptape/drivers/vector/local_vector_store_driver.md) can be used to load and query data from memory. Here is a complete example of how the Driver can be used to load a webpage into the Driver and query it later:

```python
import os 
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader


# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = LocalVectorStoreDriver(embedding_driver=embedding_driver)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=100).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
[vector_store_driver.upsert_text_artifact(a, namespace="griptape") for a in artifacts]

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Griptape Cloud Knowledge Base

The [GriptapeCloudKnowledgeBaseVectorStoreDriver](../../reference/griptape/drivers/vector/griptape_cloud_knowledge_base_vector_store_driver.md) can be used to query data from a Griptape Cloud Knowledge Base. Loading into Knowledge Bases is not supported at this time, only querying. Here is a complete example of how the Driver can be used to query an existing Knowledge Base:

```python
import os 
from griptape.drivers import GriptapeCloudKnowledgeBaseVectorStoreDriver


# Initialize environment variables
gt_cloud_api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
gt_cloud_knowledge_base_id = os.environ["GRIPTAPE_CLOUD_KB_ID"]

vector_store_driver = GriptapeCloudKnowledgeBaseVectorStoreDriver(api_key=gt_cloud_api_key, knowledge_base_id=gt_cloud_knowledge_base_id)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Pinecone

!!! info
    This Driver requires the `drivers-vector-pinecone` [extra](../index.md#extras).

The [PineconeVectorStoreDriver](../../reference/griptape/drivers/vector/pinecone_vector_store_driver.md) supports the [Pinecone vector database](https://www.pinecone.io/).

Here is an example of how the Driver can be used to load and query information in a Pinecone cluster:

```python
import os 
from griptape.drivers import PineconeVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader


# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = PineconeVectorStoreDriver(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT"],
    index_name=os.environ["PINECONE_INDEX_NAME"],
    embedding_driver=embedding_driver,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=100).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
[vector_store_driver.upsert_text_artifact(a, namespace="griptape") for a in artifacts]

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Marqo

!!! info
    This Driver requires the `drivers-vector-marqo` [extra](../index.md#extras).

The [MarqoVectorStoreDriver](../../reference/griptape/drivers/vector/marqo_vector_store_driver.md) supports the Marqo vector database.

Here is an example of how the Driver can be used to load and query information in a Marqo cluster:

```python
import os
from griptape.drivers import MarqoVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])
prompt_driver = OpenAiChatPromptDriver(model="gpt-3.5-turbo")

# Define the namespace
namespace = 'griptape-ai'

# Initialize the Vector Store Driver
vector_store_driver = MarqoVectorStoreDriver(
    api_key=os.environ["MARQO_API_KEY"],
    url=os.environ["MARQO_URL"],
    index=os.environ["MARQO_INDEX_NAME"],
    embedding_driver=embedding_driver,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Mongodb Atlas

!!! info
    This Driver requires the `drivers-vector-mongodb` [extra](../index.md#extras).

The [MongodbAtlasVectorStoreDriver](../../reference/griptape/drivers/vector/mongodb_atlas_vector_store_driver.md) provides support for storing vector data in a MongoDB Atlas database.

Here is an example of how the Driver can be used to load and query information in a MongoDb Atlas Cluster:

```python
from griptape.drivers import MongoDbAtlasVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
import os

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

host = os.environ["MONGODB_HOST"]
username = os.environ["MONGODB_USERNAME"]
password = os.environ["MONGODB_PASSWORD"]
database_name = os.environ["MONGODB_DATABASE_NAME"]
collection_name = os.environ[ "MONGODB_COLLECTION_NAME"]
index_name = os.environ["MONGODB_INDEX_NAME"]
vector_path = os.environ["MONGODB_VECTOR_PATH"]

# Initialize the Vector Store Driver
vector_store_driver = MongoDbAtlasVectorStoreDriver(
    connection_string=f"mongodb+srv://{username}:{password}@{host}/{database_name}",
    database_name=database_name,
    collection_name=collection_name,
    embedding_driver=embedding_driver,
    index_name=index_name,
    vector_path=vector_path,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

The format for creating a vector index should look similar to the following:
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "<path_to_vector>",
      "similarity": "euclidean",
      "type": "vector"
    },
    {
      "path": "namespace",
      "type": "filter"
    }
  ]
}
```
Replace `path_to_vector` with the expected field name where the vector content will be.

### Azure MongoDB

!!! info
    This Driver requires the `drivers-vector-mongodb` [extra](../index.md#extras).

The [AzureMongoDbVectorStoreDriver](../../reference/griptape/drivers/vector/azure_mongodb_vector_store_driver.md) provides support for storing vector data in an Azure CosmosDb database account using the MongoDb vCore API

Here is an example of how the Driver can be used to load and query information in an Azure CosmosDb MongoDb vCore database. It is very similar to the Driver for [MongoDb Atlas](#mongodb-atlas):

```python
from griptape.drivers import AzureMongoDbVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
import os

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

azure_host = os.environ["AZURE_MONGODB_HOST"]
username = os.environ["AZURE_MONGODB_USERNAME"]
password = os.environ["AZURE_MONGODB_PASSWORD"]
database_name = os.environ["AZURE_MONGODB_DATABASE_NAME"]
collection_name = os.environ["AZURE_MONGODB_COLLECTION_NAME"]
index_name = os.environ["AZURE_MONGODB_INDEX_NAME"]
vector_path = os.environ["AZURE_MONGODB_VECTOR_PATH"]

# Initialize the Vector Store Driver
vector_store_driver = AzureMongoDbVectorStoreDriver(
    connection_string=f"mongodb+srv://{username}:{password}@{azure_host}/{database_name}?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000",
    database_name=database_name,
    collection_name=collection_name,
    embedding_driver=embedding_driver,
    index_name=index_name,
    vector_path=vector_path,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Redis

!!! info
    This Driver requires the `drivers-vector-redis` [extra](../index.md#extras).

The [RedisVectorStoreDriver](../../reference/griptape/drivers/vector/redis_vector_store_driver.md) integrates with the Redis vector storage system.

Here is an example of how the Driver can be used to load and query information in a Redis Cluster:

```python
import os
from griptape.drivers import RedisVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
import numpy as np  # Assuming you'd use numpy to create a dummy vector for the sake of example.

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = RedisVectorStoreDriver(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    password=os.environ["REDIS_PASSWORD"],
    index=os.environ["REDIS_INDEX"],
    embedding_driver=embedding_driver,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

The format for creating a vector index should be similar to the following:
```
FT.CREATE idx:griptape ON hash PREFIX 1 "griptape:" SCHEMA namespace TAG vector VECTOR FLAT 6 TYPE FLOAT32 DIM 1536 DISTANCE_METRIC COSINE
```

### OpenSearch

!!! info
    This Driver requires the `drivers-vector-opensearch` [extra](../index.md#extras).

The [OpenSearchVectorStoreDriver](../../reference/griptape/drivers/vector/opensearch_vector_store_driver.md) integrates with the OpenSearch platform, allowing for storage, retrieval, and querying of vector data.

Here is an example of how the Driver can be used to load and query information in an OpenSearch Cluster:

```python
import os
import boto3
from griptape.drivers import AmazonOpenSearchVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = AmazonOpenSearchVectorStoreDriver(
    host=os.environ["AMAZON_OPENSEARCH_HOST"],
    index_name=os.environ["AMAZON_OPENSEARCH_INDEX_NAME"],
    session=boto3.Session(),
    embedding_driver=embedding_driver,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

The body mappings for creating a vector index should look similar to the following:
```json
{
    "mappings": {
        "properties": {
            "vector": {"type": "knn_vector", "dimension": 1536},
            "namespace": {"type": "keyword"},
            "metadata": {"type": "object", "enabled": true}
        }
    }
}
```

### PGVector

!!! info
    This Driver requires the `drivers-vector-postgresql` [extra](../index.md#extras).

The [PGVectorVectorStoreDriver](../../reference/griptape/drivers/vector/pgvector_vector_store_driver.md) integrates with PGVector, a vector storage and search extension for Postgres. While Griptape will handle enabling the extension, PGVector must be installed and ready for use in your Postgres instance before using this Vector Store Driver.

Here is an example of how the Driver can be used to load and query information in a Postgres database:

```python 
import os 
from griptape.drivers import PgVectorVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver.
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

db_user = os.environ["POSTGRES_USER"]
db_pass = os.environ["POSTGRES_PASSWORD"]
db_host = os.environ["POSTGRES_HOST"]
db_port = os.environ["POSTGRES_PORT"]
db_name = os.environ["POSTGRES_DB"]
db_connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
vector_store_driver = PgVectorVectorStoreDriver(
    connection_string=db_connection_string,
    embedding_driver=embedding_driver,
    table_name="griptape_vectors",
)

# Install required Postgres extensions and create database schema.
vector_store_driver.setup()

# Load Artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Qdrant

!!! info
    This Driver requires the `drivers-vector-qdrant` [extra](../index.md#extras).

The QdrantVectorStoreDriver supports the [Qdrant vector database](https://qdrant.tech/).

Here is an example of how the Driver can be used to query information in a Qdrant collection:

```python
import os
from griptape.drivers import QdrantVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

# Set up environment variables
host = os.environ["QDRANT_CLUSTER_ENDPOINT"]
api_key = os.environ["QDRANT_CLUSTER_API_KEY"]

# Initialize an Embedding Driver.
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = QdrantVectorStoreDriver(
    url=host,
    collection_name="griptape",
    content_payload_key="content",
    embedding_driver=embedding_driver,
    api_key=api_key,
)

# Load Artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")

# Recreate Qdrant collection
vector_store_driver.client.recreate_collection(
    collection_name=vector_store_driver.collection_name,
    vectors_config={
        "size": 1536,
        "distance": vector_store_driver.distance
    },
)

# Upsert Artifacts into the Vector Store Driver
[vector_store_driver.upsert_text_artifact(a, namespace="griptape") for a in artifacts]

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```
