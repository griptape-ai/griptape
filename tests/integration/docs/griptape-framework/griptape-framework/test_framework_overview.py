import re
import os


class TestFrameworkOverview:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/
    """

    def test_simple_agent(self):
        from griptape.structures import Agent

        agent = Agent()
        result = agent.run("write me a haiku about griptape")

        assert result.output is not None

    def test_simple_agent_with_tools(self):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        calculator = Calculator()

        agent = Agent(tools=[calculator])

        result = agent.run("what is 7^12")

        assert result.output is not None
        assert re.search("13,?841,?287,?201", result.output.to_text())

    def test_simple_pipeline(self):
        from griptape.memory.structure import ConversationMemory
        from griptape.structures import Pipeline
        from griptape.tasks import ToolkitTask, PromptTask
        from griptape.tools import WebScraper, FileManager

        # Pipelines represent sequences of tasks.
        pipeline = Pipeline(memory=ConversationMemory())

        pipeline.add_tasks(
            # Load up the first argument from `pipeline.run`.
            ToolkitTask(
                "{{ args[0] }}",
                # Add tools for web scraping, and file management
                tools=[WebScraper(), FileManager()],
            ),
            # Augment `input` from the previous task.
            PromptTask("Say the following in spanish: {{ input }}"),
        )

        pipeline.run(
            "Load https://www.griptape.ai, summarize it, and store it in griptape.txt"
        )

        assert os.path.exists("griptape.txt")

        with open("griptape.txt", "r", encoding="utf-8") as file:
            contents = file.read()

            assert re.search("tape", contents, re.IGNORECASE)
