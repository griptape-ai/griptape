from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import CsvExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ExtractionTask

# Instantiate the CSV extraction engine
csv_extraction_engine = CsvExtractionEngine(prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"))

# Define some unstructured data and columns
csv_data = """
Alice, 28, lives in New York.
Bob, 35 lives in California.
Charlie is 40 and lives in Texas.
"""

columns = ["Name", "Age", "Address"]


# Create an agent and add the ExtractionTask to it
agent = Agent()
agent.add_task(
    ExtractionTask(
        extraction_engine=csv_extraction_engine,
        args={"column_names": columns},
    )
)

# Run the agent
agent.run(csv_data)
