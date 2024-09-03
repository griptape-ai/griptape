from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, VectorStoreTool

vector_store_driver = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(),
)

artifacts = WebLoader().load("https://www.griptape.ai")

vector_store_driver.upsert_text_artifacts({"griptape": artifacts})
vector_db = VectorStoreTool(
    description="This DB has information about the Griptape Python framework",
    vector_store_driver=vector_store_driver,
    query_params={"namespace": "griptape"},
    off_prompt=True,
)

agent = Agent(tools=[vector_db, PromptSummaryTool()])

agent.run("what is Griptape?")
