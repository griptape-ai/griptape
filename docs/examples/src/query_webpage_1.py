import os

from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"]))

artifacts = WebLoader(max_tokens=100).load("https://www.griptape.ai")
if isinstance(artifacts, ErrorArtifact):
    raise Exception(artifacts.value)

for a in artifacts:
    vector_store.upsert_text_artifact(a, namespace="griptape")

results = vector_store.query("creativity", count=3, namespace="griptape")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
