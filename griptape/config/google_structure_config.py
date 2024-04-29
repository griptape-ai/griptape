from attrs import define, field, Factory

from griptape.config import StructureConfig
from griptape.drivers import GoogleEmbeddingDriver, GooglePromptDriver, LocalVectorStoreDriver


@define
class GoogleStructureConfig(StructureConfig):
    prompt_driver: GooglePromptDriver = field(
        default=Factory(lambda: GooglePromptDriver(model="gemini-pro")), metadata={"serializable": True}
    )
    embedding_driver: GoogleEmbeddingDriver = field(
        default=Factory(lambda: GoogleEmbeddingDriver(model="models/embedding-001")), metadata={"serializable": True}
    )
    vector_store_driver: LocalVectorStoreDriver = field(
        default=Factory(
            lambda: LocalVectorStoreDriver(embedding_driver=GoogleEmbeddingDriver(model="models/embedding-001"))
        ),
        metadata={"serializable": True},
    )
