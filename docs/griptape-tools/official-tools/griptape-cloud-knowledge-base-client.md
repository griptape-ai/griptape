## Overview

The `GriptapeCloudKnowledgeBaseClient` is an advanced Tool designed to streamline how organizations access and search their data. It leverages a RAG pipeline and vector stores hosted in [Griptape Cloud](https://cloud.griptape.ai) and allows users to perform intuitive searches across a centralized [Knowledge Base](https://cloud.griptape.ai/knowledge-bases) that consolidates various data sources such as Confluence, Google Docs, and web pages. This integration empowers users to connect and search through information pools, making it easier to find relevant data quickly.

Griptape utilizes this technology to enhance organizational efficiency and knowledge sharing. By connecting diverse documentation and data sources into a single searchable repository, the `GriptapeCloudKnowledgeBaseClient` helps facilitate faster decision-making while improving productivity.

**Note:** This tool requires a [Knowledge Base](https://cloud.griptape.ai/knowledge-bases) hosted in Griptape Cloud and an [API Key](https://cloud.griptape.ai/keys) for access.

```python
import os
from griptape.structures import Agent
from griptape.tools import GriptapeCloudKnowledgeBaseClient
from dotenv import load_dotenv

load_dotenv()

knowledge_base_client = GriptapeCloudKnowledgeBaseClient(
    description="Contains information about the company and its operations",
    api_key=os.environ["GT_CLOUD_API_KEY"],
    knowledge_base_id=os.environ["GT_CLOUD_KB_ID"],
    off_prompt=False
)

agent = Agent(
    tools=[
        knowledge_base_client,
    ]
)

agent.run("What is the company's corporate travel policy?")
```
