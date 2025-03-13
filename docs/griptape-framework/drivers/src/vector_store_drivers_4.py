import os

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.vector.marqo import MarqoVectorStoreDriver
from griptape.loaders import WebLoader

# Initialize an Embedding Driver
embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])
prompt_driver = OpenAiChatPromptDriver(model="gpt-3.5-turbo")

# Define the namespace
namespace = "griptape-ai"

# Initialize the Vector Store Driver
vector_store_driver = MarqoVectorStoreDriver(
    api_key=os.environ["MARQO_API_KEY"],
    url=os.environ["MARQO_URL"],
    index=os.environ["MARQO_INDEX_NAME"],
    embedding_driver=embedding_driver,
)

# Load Artifacts from the web
artifact = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker(max_tokens=200).chunk(artifact)

# Upsert Artifacts into the Vector Store Driver
vector_store_driver.upsert_collection(
    {
        "griptape": chunks,
    }
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
