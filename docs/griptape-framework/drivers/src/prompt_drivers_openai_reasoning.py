import os

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(
        api_key=os.environ["OPENAI_API_KEY"],
        model="o3-mini",
        reasoning_effort="medium",
    ),
)

agent.run("""Write a bash script that takes a matrix represented as a string with
format '[1,2],[3,4],[5,6]' and prints the transpose in the same format.""")
