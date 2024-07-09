```python
import os 
from griptape.artifacts import BaseArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader


vector_store = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(
        api_key=os.environ["OPENAI_API_KEY"]
    )
)

[
    vector_store.upsert_text_artifact(a, namespace="griptape")
    for a in WebLoader(max_tokens=100).load("https://www.griptape.ai")
]

results = vector_store.query(
    "creativity",
    count=3,
    namespace="griptape"
)

values = [BaseArtifact.from_json(r.meta["artifact"]).value for r in results]

print("\n\n".join(values))
```