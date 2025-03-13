import os

import boto3

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.amazon_opensearch import AmazonOpenSearchVectorStoreDriver
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
artifact = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker(max_tokens=200).chunk(artifact)

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_collection(
    {
        "griptape": chunks,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
