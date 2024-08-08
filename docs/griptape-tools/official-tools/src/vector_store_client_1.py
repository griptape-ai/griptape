from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import TaskMemoryClient, VectorStoreClient

vector_store_driver = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(),
)

artifacts = WebLoader().load("https://www.griptape.ai")
if isinstance(artifacts, ErrorArtifact):
    raise Exception(artifacts.value)

vector_store_driver.upsert_text_artifacts({"griptape": artifacts})
vector_db = VectorStoreClient(
    description="This DB has information about the Griptape Python framework",
    vector_store_driver=vector_store_driver,
    query_params={"namespace": "griptape"},
    off_prompt=True,
)

agent = Agent(tools=[vector_db, TaskMemoryClient(off_prompt=False)])

agent.run("what is Griptape?")
