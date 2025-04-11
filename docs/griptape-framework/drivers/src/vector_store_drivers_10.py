import os

from qdrant_client.http.models import Distance, VectorParams

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.qdrant import QdrantVectorStoreDriver
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
artifact = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker(max_tokens=100).chunk(artifact)

# Recreate Qdrant collection
vector_store_driver.client.recreate_collection(
    collection_name=vector_store_driver.collection_name,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_collection({"griptape": chunks})

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
