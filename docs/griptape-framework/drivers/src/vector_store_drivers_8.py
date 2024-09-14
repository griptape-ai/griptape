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
