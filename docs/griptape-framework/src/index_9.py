from typing import cast

from pydantic import BaseModel

from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask


class Output(BaseModel):
    answer: str


task = PromptTask(
    input="You are speaking to: {{ user_name }}. User said: {{ args[0] }}",
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    context={"user_name": "Collin"},
    rulesets=[
        Ruleset(
            name="Backstory",
            rules=[
                Rule("Your name is Oswald."),
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
)

task_output_value = cast("Output", task.run("Hi there!").value)

print(task_output_value.answer)
