from pydantic import BaseModel
from rich.pretty import pprint

from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver
from griptape.memory.structure import ConversationMemory
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask
from griptape.tools import WebScraperTool, WebSearchTool


class Feature(BaseModel):
    name: str
    description: str
    emoji: str


class Output(BaseModel):
    answer: str
    key_features: list[Feature]


task = PromptTask(
    id="project-research",
    input="You are speaking to: {{ user_name }}. User said: {{ args[0] }}",
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    context={"user_name": "Collin"},
    rulesets=[
        Ruleset(
            name="Backstory",
            rules=[
                Rule("Your name is Oswald."),
                Rule("You run 'Oswald's Open Source', a company for helping people learn about open source."),
            ],
        ),
        Ruleset(
            name="Behavior",
            rules=[
                Rule("Introduce yourself at the start of the conversation."),
            ],
        ),
    ],
    output_schema=Output,
    tools=[
        WebSearchTool(
            web_search_driver=DuckDuckGoWebSearchDriver(),
        ),
        WebScraperTool(),
    ],
    conversation_memory=ConversationMemory(),
)

output = task.run("Tell me about the python framework Griptape.")

pprint(output.value)
