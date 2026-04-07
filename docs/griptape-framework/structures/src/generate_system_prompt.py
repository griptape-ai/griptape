from textwrap import dedent

from griptape.rules import Rule
from griptape.structures import Pipeline
from griptape.tasks.prompt_task import PromptTask

pipeline = Pipeline(
    tasks=[
        PromptTask(
            rules=[Rule("Your favorite color is blue")],  # Will be ignored!
            generate_system_template=lambda _: dedent("""
                Employment:
                    - Behave like a polite customer support agent
                    - Act like you work for company SkaterWorld, Inc.
                    - Discuss only topics related to skateboarding
                    - Limit your response to fewer than 5 sentences.

                Background:
                    - Your name is Todd
                """),
        )
    ]
)

pipeline.run("What is your name and favorite color?")
