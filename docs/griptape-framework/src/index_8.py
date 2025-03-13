import json
from typing import TYPE_CHECKING, cast

from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.rules import JsonSchemaRule, Rule, Ruleset
from griptape.tasks import PromptTask

if TYPE_CHECKING:
    from griptape.artifacts.text_artifact import TextArtifact

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
        Ruleset(
            name="Output Format",
            rules=[
                JsonSchemaRule(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                        },
                        "required": ["answer"],
                    }
                )
            ],
        ),
    ],
)

task_output_value = cast("TextArtifact", task.run("Hi there!")).value


print(json.dumps(json.loads(task_output_value), indent=2))
