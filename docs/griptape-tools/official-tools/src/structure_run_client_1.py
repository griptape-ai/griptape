import os

from griptape.drivers import GriptapeCloudStructureRunDriver
from griptape.structures import Agent
from griptape.tools import StructureRunClient

base_url = os.environ["GRIPTAPE_CLOUD_BASE_URL"]
api_key = os.environ["GRIPTAPE_CLOUD_API_KEY"]
structure_id = os.environ["GRIPTAPE_CLOUD_STRUCTURE_ID"]

structure_run_tool = StructureRunClient(
    description="RAG Expert Agent - Structure to invoke with natural language queries about the topic of Retrieval Augmented Generation",
    driver=GriptapeCloudStructureRunDriver(
        base_url=base_url,
        api_key=api_key,
        structure_id=structure_id,
    ),
)

# Set up an agent using the StructureRunClient tool
agent = Agent(tools=[structure_run_tool])

# Task: Ask the Griptape Cloud Hosted Structure about modular RAG
agent.run("what is modular RAG?")
