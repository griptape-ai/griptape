from griptape.config import StructureConfig
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o", temperature=0.3),
    ),
    input="You will be provided with a tweet, and your task is to classify its sentiment as positive, neutral, or negative. Tweet: {{ args[0] }}",
    rules=[Rule(value="Output only the sentiment.")],
)

agent.run("I loved the new Batman movie!")
