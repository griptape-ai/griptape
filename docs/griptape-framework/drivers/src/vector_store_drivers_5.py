import os

from griptape.drivers import MongoDbAtlasVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

host = os.environ["MONGODB_HOST"]
username = os.environ["MONGODB_USERNAME"]
password = os.environ["MONGODB_PASSWORD"]
database_name = os.environ["MONGODB_DATABASE_NAME"]
collection_name = os.environ["MONGODB_COLLECTION_NAME"]
index_name = os.environ["MONGODB_INDEX_NAME"]
vector_path = os.environ["MONGODB_VECTOR_PATH"]

# Initialize the Vector Store Driver
vector_store_driver = MongoDbAtlasVectorStoreDriver(
    connection_string=f"mongodb+srv://{username}:{password}@{host}/{database_name}",
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
