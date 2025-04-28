from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1", temperature=0.3),
    input="You will be provided with a tweet, and your task is to classify its sentiment as positive, neutral, or negative. Tweet: {{ args[0] }}",
    rules=[Rule(value="Output only the sentiment.")],
)

agent.run("I loved the new Batman movie!")
