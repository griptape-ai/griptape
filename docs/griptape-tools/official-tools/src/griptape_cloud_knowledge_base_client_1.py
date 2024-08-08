import os

from griptape.structures import Agent
from griptape.tools import GriptapeCloudKnowledgeBaseClient

knowledge_base_client = GriptapeCloudKnowledgeBaseClient(
    description="Contains information about the company and its operations",
    api_key=os.environ["GRIPTAPE_CLOUD_API_KEY"],
    knowledge_base_id=os.environ["GRIPTAPE_CLOUD_KB_ID"],
)

agent = Agent(
    tools=[
        knowledge_base_client,
    ]
)

agent.run("What is the company's corporate travel policy?")
