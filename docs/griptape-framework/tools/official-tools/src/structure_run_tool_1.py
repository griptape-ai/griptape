from griptape.drivers.structure_run.local import LocalStructureRunDriver
from griptape.rules import Rule
from griptape.structures import Agent
from griptape.tools import StructureRunTool


def build_rag_expert() -> Agent:
    return Agent(
        rules=[
            Rule(
                value="You are an expert on Retrieval Augmented Generation (RAG).",
            )
        ],
    )


structure_run_tool = StructureRunTool(
    description="RAG Expert Agent - Structure to invoke with natural language queries about the topic of Retrieval Augmented Generation",
    structure_run_driver=LocalStructureRunDriver(
        create_structure=build_rag_expert,
    ),
)

# Set up an agent using the StructureRunTool tool
agent = Agent(tools=[structure_run_tool])

# Task: Ask the RAG Expert Structure about modular RAG
agent.run("what is modular RAG?")
