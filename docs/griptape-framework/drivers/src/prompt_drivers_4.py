from griptape.config import StructureConfig
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(
            base_url="http://127.0.0.1:1234/v1", model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF", stream=True
        )
    ),
    rules=[Rule(value="You are a helpful coding assistant.")],
)

agent.run("How do I init and update a git submodule?")
