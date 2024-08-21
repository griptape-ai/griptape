from schema import Schema

from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import JsonExtractionEngine

# Define a schema for extraction
user_schema = Schema([{"name": str, "age": int, "location": str}]).json_schema("UserSchema")

json_engine = JsonExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"), template_schema=user_schema
)

# Define some unstructured data
sample_json_text = """
Alice (Age 28) lives in New York.
Bob (Age 35) lives in California.
"""


# Extract data using the engine
result = json_engine.extract_text(sample_json_text)

for artifact in result:
    print(artifact.value)
