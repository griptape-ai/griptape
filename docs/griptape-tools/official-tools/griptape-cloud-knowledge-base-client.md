## Overview

The `GriptapeCloudKnowledgeBaseClient` is an advanced Tool to retrieve data from a RAG pipeline and vector stores hosted in [Griptape Cloud](https://cloud.griptape.ai). It performs searches across a centralized [Knowledge Base](https://cloud.griptape.ai/knowledge-bases) that can consist of various data sources such as Confluence, Google Docs, and web pages.

**Note:** This tool requires a [Knowledge Base](https://cloud.griptape.ai/knowledge-bases) hosted in Griptape Cloud and an [API Key](https://cloud.griptape.ai/keys) for access.

```python
import os
from griptape.structures import Agent
from griptape.tools import GriptapeCloudKnowledgeBaseClient

knowledge_base_client = GriptapeCloudKnowledgeBaseClient(
    description="Contains information about the company and its operations",
    api_key=os.environ["INTEG_GRIPTAPE_CLOUD_API_KEY"],
    knowledge_base_id=os.environ["INTEG_GRIPTAPE_CLOUD_KB_ID"],
    off_prompt=False
)

agent = Agent(
    tools=[
        knowledge_base_client,
    ]
)

agent.run("What is the company's corporate travel policy?")
```
