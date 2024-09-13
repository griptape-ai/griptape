import os

from griptape.chunkers import TextChunker
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"]))

artifacts = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker().chunk(artifacts)

for chunk in chunks:
    vector_store.upsert_text_artifact(chunk, namespace="griptape")

results = vector_store.query("creativity", count=3, namespace="griptape")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
