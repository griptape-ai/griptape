import json

from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import JsonExtractionEngine
from griptape.loaders import WebLoader

# Define a schema for extraction
json_engine = JsonExtractionEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    template_schema=Schema(
        {
            Literal("model", description="Name of an LLM model."): str,
            Literal("notes", description="Any notes of substance about the model."): Schema([str]),
        }
    ).json_schema("ProductSchema"),
)

# Load data from the web
web_data = WebLoader().load("https://en.wikipedia.org/wiki/Large_language_model")

if isinstance(web_data, ErrorArtifact):
    raise Exception(web_data.value)

# Extract data using the engine
result = json_engine.extract_artifacts(ListArtifact(web_data))

for artifact in result:
    print(json.dumps(artifact.value, indent=2))
