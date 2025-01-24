from griptape.configs import Defaults
from griptape.configs.drivers import OpenAiDriversConfig
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.amazon_bedrock import AmazonBedrockPromptDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.structures import Agent
from griptape.tools import FileManagerTool, QueryTool, WebScraperTool

Defaults.drivers_config = OpenAiDriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
)

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

agent = Agent(
    tools=[
        WebScraperTool(off_prompt=True),
        QueryTool(
            off_prompt=True,
            prompt_driver=AmazonBedrockPromptDriver(model="anthropic.claude-3-haiku-20240307-v1:0"),
        ),
        FileManagerTool(off_prompt=True),
    ],
)

agent.run(
    "Use this page https://en.wikipedia.org/wiki/Elden_Ring to find how many copies of Elden Ring have been sold, and then save the result to a file."
)
