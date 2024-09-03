import os

from griptape.drivers import AzureMongoDbVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

azure_host = os.environ["AZURE_MONGODB_HOST"]
username = os.environ["AZURE_MONGODB_USERNAME"]
password = os.environ["AZURE_MONGODB_PASSWORD"]
database_name = os.environ["AZURE_MONGODB_DATABASE_NAME"]
collection_name = os.environ["AZURE_MONGODB_COLLECTION_NAME"]
index_name = os.environ["AZURE_MONGODB_INDEX_NAME"]
vector_path = os.environ["AZURE_MONGODB_VECTOR_PATH"]

# Initialize the Vector Store Driver
vector_store_driver = AzureMongoDbVectorStoreDriver(
    connection_string=f"mongodb+srv://{username}:{password}@{azure_host}/{database_name}?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000",
    database_name=database_name,
    collection_name=collection_name,
    embedding_driver=embedding_driver,
    index_name=index_name,
    vector_path=vector_path,
)

# Load Artifacts from the web
artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
