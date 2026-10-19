import os

from griptape.artifacts import TextArtifact
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver

embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])
vector_store_driver = LocalVectorStoreDriver(embedding_driver=embedding_driver)
text = "Griptape is an enterprise AI framework."

vector_store_driver.upsert_collection({"upsert": [TextArtifact(text), TextArtifact(text)]})
vector_store_driver.insert_collection({"insert": [TextArtifact(text), TextArtifact(text)]})

print(f"upsert entries: {len(vector_store_driver.load_entries(namespace='upsert'))}")
print(f"insert entries: {len(vector_store_driver.load_entries(namespace='insert'))}")
