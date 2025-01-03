import schema
from rich.pretty import pprint

from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    tasks=[
        PromptTask(
            prompt_driver=OpenAiChatPromptDriver(
                model="gpt-4o",
                structured_output_strategy="native",  # optional
            ),
            output_schema=schema.Schema(
                {
                    "steps": [schema.Schema({"explanation": str, "output": str})],
                    "final_answer": str,
                }
            ),
            rules=[
                Rule("You are a helpful math tutor. Guide the user through the solution step by step."),
            ],
        )
    ]
)

output = pipeline.run("How can I solve 8x + 7 = -23").output.value


pprint(output)
