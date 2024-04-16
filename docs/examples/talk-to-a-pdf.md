This example demonstrates how to vectorize a PDF of the [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf) paper and setup a Griptape agent with rules and the [VectorStoreClient](../reference/griptape/tools/vector_store_client/tool.md) tool to use it during conversations.

```python
import os 
import io
import requests
from griptape.engines import VectorQueryEngine
from griptape.loaders import PdfLoader
from griptape.structures import Agent
from griptape.tools import VectorStoreClient
from griptape.utils import Chat
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver


namespace = "attention"

response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")

engine = VectorQueryEngine(
    prompt_driver=OpenAiChatPromptDriver(
        model="gpt-3.5-turbo",
    ),
    vector_store_driver=LocalVectorStoreDriver(
        embedding_driver=OpenAiEmbeddingDriver(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    )
)

engine.vector_store_driver.upsert_text_artifacts(
    {
        namespace: PdfLoader().load(response.content)
    }
)

vector_store_tool = VectorStoreClient(
    description="Contains information about the Attention Is All You Need paper. "
                "Use it to answer any related questions.",
    query_engine=engine,
    namespace=namespace,
    off_prompt=False
)

agent = Agent(
    tools=[vector_store_tool]
)

Chat(agent).start()
```
