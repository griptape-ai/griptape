import re
import os
from textwrap import dedent
from json import loads
from griptape.rules import Ruleset, Rule
from griptape.drivers import OpenAiChatPromptDriver, AnthropicPromptDriver

OUTPUT_RULESET = Ruleset(
    name="Output Format",
    rules=[
        Rule(
            value=dedent(
                """Your answer MUST be the following format: 
                {
                    "task_output": "<task output>",
                    "task_result": "<success|failure>",
                }
                If there is an error in the task, task_result should be "failure".
                """
            )
        )
    ],
)

PROMPT_DRIVERS = [
    OpenAiChatPromptDriver(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"]),
    OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"]),
    AnthropicPromptDriver(model='claude-2', api_key=os.environ["ANTHROPIC_API_KEY"]),
]

def prompt_driver_id_fn(prompt_driver) -> str:
    return f'{prompt_driver.__class__.__name__}-{prompt_driver.model}'


def run_structure(structure, prompt) -> dict:
    result = structure.run(prompt)
    response_matches = re.findall(r"[^{]*({.*})", result.output.to_text(), re.DOTALL)
    if response_matches:
        return loads(response_matches[0], strict=False)
    raise ValueError("No valid response found")
