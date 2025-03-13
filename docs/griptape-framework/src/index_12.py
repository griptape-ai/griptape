from pydantic import BaseModel
from rich.pretty import pprint

from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver
from griptape.rules import Rule, Ruleset
from griptape.structures import Workflow
from griptape.tasks import PromptTask
from griptape.tools import WebScraperTool, WebSearchTool


class Feature(BaseModel):
    name: str
    description: str
    emoji: str


class Output(BaseModel):
    answer: str
    key_features: list[Feature]


projects = ["django", "flask", "fastapi", "litestar"]

workflow = Workflow(
    rulesets=[
        Ruleset(
            name="Backstory",
            rules=[
                Rule("Your name is Oswald."),
                Rule("You run 'Oswald's Open Source', a company for helping people learn about open source."),
            ],
        ),
    ],
)
prompt_driver = OpenAiChatPromptDriver(model="gpt-4o")

for project in projects:
    task = PromptTask(
        id=f"project-research-{project}",
        input="Tell me about the open source project: {{ project }}.",
        prompt_driver=prompt_driver,
        context={"project": project},
        output_schema=Output,
        tools=[
            WebSearchTool(
                web_search_driver=DuckDuckGoWebSearchDriver(),
            ),
            WebScraperTool(),
        ],
    )
    workflow.add_task(task)

workflow.run()

for output in workflow.outputs:
    pprint(output.value)
