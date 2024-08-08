import os

from griptape.drivers import OpenAiEmbeddingDriver, PgVectorVectorStoreDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver.
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])

db_user = os.environ["POSTGRES_USER"]
db_pass = os.environ["POSTGRES_PASSWORD"]
db_host = os.environ["POSTGRES_HOST"]
db_port = os.environ["POSTGRES_PORT"]
db_name = os.environ["POSTGRES_DB"]
db_connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
vector_store_driver = PgVectorVectorStoreDriver(
    connection_string=db_connection_string,
    embedding_driver=embedding_driver,
    table_name="griptape_vectors",
)

# Install required Postgres extensions and create database schema.
vector_store_driver.setup()

# Load Artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_text_artifacts(
    {
        "griptape": artifacts,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
