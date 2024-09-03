import os

from griptape.drivers import OpenAiEmbeddingDriver, QdrantVectorStoreDriver
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
    vectors_config={"size": 1536, "distance": vector_store_driver.distance},
)

# Upsert Artifacts into the Vector Store Driver
[vector_store_driver.upsert_text_artifact(a, namespace="griptape") for a in artifacts]

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
