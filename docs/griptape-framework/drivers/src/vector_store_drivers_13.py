from attrs import define, field

from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.drivers.embedding.base_embedding_driver import VectorOperation
from griptape.drivers.vector.milvus import MilvusVectorStoreDriver


@define
class SimpleEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(default="simple", kw_only=True)

    def try_embed_chunk(self, chunk: str, *, vector_operation: VectorOperation | None = None) -> list[float]:
        text = chunk.lower()

        return [float("milvus" in text), float("griptape" in text)]


vector_store_driver = MilvusVectorStoreDriver(
    collection_name="griptape_docs",
    embedding_driver=SimpleEmbeddingDriver(),
)

vector_store_driver.upsert(
    "Milvus stores vectors locally with Milvus Lite.",
    namespace="docs",
    meta={"source": "local"},
)
vector_store_driver.upsert(
    "Griptape drivers share a common vector store interface.",
    namespace="docs",
    meta={"source": "framework"},
)

results = vector_store_driver.query("Milvus local storage", namespace="docs", filter={"source": "local"})

print(results[0].to_artifact().value)
