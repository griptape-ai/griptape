from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.engines import CsvExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ExtractionTask

# Instantiate the CSV extraction engine
csv_extraction_engine = CsvExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"), column_names=["Name", "Age", "Address"]
)

# Define some unstructured data and columns
csv_data = """
Alice, 28, lives in New York.
Bob, 35 lives in California.
Charlie is 40 and lives in Texas.
"""


# Create an agent and add the ExtractionTask to it
agent = Agent()
agent.add_task(
    ExtractionTask(
        extraction_engine=csv_extraction_engine,
    )
)

# Run the agent
agent.run(csv_data)
