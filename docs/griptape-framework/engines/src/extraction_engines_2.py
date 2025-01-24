import json

from schema import Literal, Schema

from griptape.artifacts import ListArtifact
from griptape.chunkers import TextChunker
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
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
chunks = TextChunker().chunk(web_data)


# Extract data using the engine
result = json_engine.extract_artifacts(ListArtifact(chunks))

for artifact in result:
    print(json.dumps(artifact.value, indent=2))
