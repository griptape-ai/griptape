import os

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.vector.marqo import MarqoVectorStoreDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import VectorStoreTool

# Define the namespace
namespace = "griptape-ai"

# # Initialize the vector store driver
vector_store = MarqoVectorStoreDriver(
    api_key=os.environ["MARQO_API_KEY"],
    url=os.environ["MARQO_URL"],
    index=os.environ["MARQO_INDEX_NAME"],
    embedding_driver=OpenAiEmbeddingDriver(),
)

# Initialize the knowledge base tool
vector_store_tool = VectorStoreTool(
    description="Contains information about the Griptape Framework from www.griptape.ai",
    vector_store_driver=vector_store,
)

# Load artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")
chunks = TextChunker().chunk(artifacts)

# Upsert the artifacts into the vector store
vector_store.upsert_collection(
    {
        namespace: chunks,
    }
)

# Initialize the agent
agent = Agent(tools=[vector_store_tool])

agent.run("What is the Griptape Framework?")
