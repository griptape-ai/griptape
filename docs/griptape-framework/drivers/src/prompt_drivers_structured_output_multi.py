import schema
from rich.pretty import pprint

from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import JsonSchemaRule
from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    tasks=[
        PromptTask(
            prompt_driver=OpenAiChatPromptDriver(
                model="gpt-4o",
                use_native_structured_output=True,
                native_structured_output_strategy="tool",
            ),
            rules=[
                JsonSchemaRule(schema.Schema({"color": "red"})),
                JsonSchemaRule(schema.Schema({"color": "blue"})),
            ],
        )
    ]
)

output = pipeline.run("Pick a color").output.value


pprint(output)
