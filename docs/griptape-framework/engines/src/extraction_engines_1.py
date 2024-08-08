from griptape.artifacts import ListArtifact
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import CsvExtractionEngine

# Initialize the CsvExtractionEngine instance
csv_engine = CsvExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
)

# Define some unstructured data
sample_text = """
Alice, 28, lives in New York.
Bob, 35 lives in California.
Charlie is 40 and lives in Texas.
"""

# Extract CSV rows using the engine
result = csv_engine.extract(sample_text, column_names=["name", "age", "location"])

if isinstance(result, ListArtifact):
    for row in result.value:
        print(row.to_text())
else:
    print(result.to_text())
