import os

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.astradb import AstraDbVectorStoreDriver
from griptape.loaders import WebLoader

# Astra DB secrets and connection parameters
api_endpoint = os.environ["ASTRA_DB_API_ENDPOINT"]
token = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
astra_db_namespace = os.environ.get("ASTRA_DB_KEYSPACE")  # optional

# Initialize an Embedding Driver.
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

vector_store_driver = AstraDbVectorStoreDriver(
    embedding_driver=embedding_driver,
    api_endpoint=api_endpoint,
    token=token,
    collection_name="griptape_test_collection",
    astra_db_namespace=astra_db_namespace,  # optional
)

# Load Artifacts from the web
artifact = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker().chunk(artifact)

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_collection({"griptape": chunks})

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
