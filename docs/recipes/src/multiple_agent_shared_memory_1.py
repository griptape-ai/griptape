import os

from griptape.configs import Defaults
from griptape.configs.drivers import AzureOpenAiDriversConfig
from griptape.drivers.embedding.openai import AzureOpenAiEmbeddingDriver
from griptape.drivers.vector.azure_mongodb import AzureMongoDbVectorStoreDriver
from griptape.structures import Agent
from griptape.tools import QueryTool, WebScraperTool

AZURE_OPENAI_ENDPOINT_1 = os.environ["AZURE_OPENAI_ENDPOINT_1"]
AZURE_OPENAI_API_KEY_1 = os.environ["AZURE_OPENAI_API_KEY_1"]

MONGODB_HOST = os.environ["MONGODB_HOST"]
MONGODB_USERNAME = os.environ["MONGODB_USERNAME"]
MONGODB_PASSWORD = os.environ["MONGODB_PASSWORD"]
MONGODB_DATABASE_NAME = os.environ["MONGODB_DATABASE_NAME"]
MONGODB_COLLECTION_NAME = os.environ["MONGODB_COLLECTION_NAME"]
MONGODB_INDEX_NAME = os.environ["MONGODB_INDEX_NAME"]
MONGODB_VECTOR_PATH = os.environ["MONGODB_VECTOR_PATH"]
MONGODB_CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}/{MONGODB_DATABASE_NAME}?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

embedding_driver = AzureOpenAiEmbeddingDriver(
    model="text-embedding-ada-002",
    azure_endpoint=AZURE_OPENAI_ENDPOINT_1,
    api_key=AZURE_OPENAI_API_KEY_1,
)

mongo_driver = AzureMongoDbVectorStoreDriver(
    connection_string=MONGODB_CONNECTION_STRING,
    database_name=MONGODB_DATABASE_NAME,
    collection_name=MONGODB_COLLECTION_NAME,
    embedding_driver=embedding_driver,
    index_name=MONGODB_INDEX_NAME,
    vector_path=MONGODB_VECTOR_PATH,
)

Defaults.drivers_config = AzureOpenAiDriversConfig(
    azure_endpoint=AZURE_OPENAI_ENDPOINT_1,
    api_key=AZURE_OPENAI_API_KEY_1,
    vector_store_driver=mongo_driver,
    embedding_driver=embedding_driver,
)

loader = Agent(
    tools=[
        WebScraperTool(off_prompt=True),
    ],
)
asker = Agent(
    tools=[
        QueryTool(off_prompt=False),
    ],
    meta_memory=loader.meta_memory,
    task_memory=loader.task_memory,
)

if __name__ == "__main__":
    loader.run(
        "Load https://medium.com/enterprise-rag/a-first-intro-to-complex-rag-retrieval-augmented-generation-a8624d70090f"
    )
    asker.run("why is retrieval augmented generation useful?")
