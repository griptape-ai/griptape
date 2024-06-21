```python title="PYTEST_IGNORE"
import os
from griptape import utils
from griptape.drivers import MarqoVectorStoreDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import VectorStoreClient
from griptape.drivers import OpenAiEmbeddingDriver

# Define the namespace
namespace = "griptape-ai"

# # Initialize the vector store driver
vector_store = MarqoVectorStoreDriver(
    api_key=os.environ["MARQO_API_KEY"],
    url=os.environ["MARQO_URL"],
    index=os.environ["MARQO_INDEX_NAME"],
    embedding_driver=OpenAiEmbeddingDriver()
)

# Initialize the knowledge base tool
vector_store_tool = VectorStoreClient(
    description="Contains information about the Griptape Framework from www.griptape.ai",
    namespace=namespace,
)

# Load artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")

# Upsert the artifacts into the vector store
vector_store.upsert_text_artifacts(
    {
        namespace: artifacts,
    }
)

# Initialize the agent
agent = Agent(tools=[vector_store_tool])

# Start the chat
utils.Chat(agent).start()
```
