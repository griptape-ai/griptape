import os

from griptape.drivers import OpenAiEmbeddingDriver, PineconeVectorStoreDriver
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
