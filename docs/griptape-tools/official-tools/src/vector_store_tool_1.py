from griptape.chunkers import TextChunker
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import VectorStoreTool

NAMESPACE = "griptape"

vector_store_driver = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(),
)

artifacts = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker().chunk(artifacts)

vector_store_driver.upsert_text_artifacts({NAMESPACE: chunks})
vector_db = VectorStoreTool(
    description="This DB has information about the Griptape Python framework",
    vector_store_driver=vector_store_driver,
    query_params={"namespace": NAMESPACE},
)

agent = Agent(tools=[vector_db])

agent.run("what is Griptape?")
