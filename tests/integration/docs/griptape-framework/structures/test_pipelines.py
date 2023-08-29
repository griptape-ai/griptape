import re


class TestPipelines:
    def test_pipelines(self):
        from griptape.memory.structure import ConversationMemory
        from griptape.tasks import PromptTask
        from griptape.structures import Pipeline

        pipeline = Pipeline(memory=ConversationMemory())

        pipeline.add_tasks(
            # take the first argument from the pipeline `run` method
            PromptTask("{{ args[0] }}"),
            # take the input from the previous task and insert it into the prompt
            PromptTask("Say the following like a pirate: {{ parent_output }}"),
        )

        result = pipeline.run("I am Scotty, who are you?")

        assert result.output is not None
        assert re.search("Ahoy", result.output.to_text(), re.IGNORECASE)

        result = pipeline.run("Who am I?")

        assert result.output is not None
        assert re.search("Scotty", result.output.to_text(), re.IGNORECASE)

    def test_prompt_context(self):
        from griptape.memory.structure import ConversationMemory
        from griptape.tasks import PromptTask
        from griptape.structures import Pipeline

        pipeline = Pipeline(memory=ConversationMemory())

        pipeline.add_tasks(
            PromptTask(
                "tell me about {{ topic }}", context={"topic": "the lord of the rings"}
            )
        )

        result = pipeline.run()

        assert result.output is not None
        assert re.search("lord", result.output.to_text(), re.IGNORECASE)

    def test_prompt_drivers(self):
        from griptape.memory.structure import ConversationMemory
        from griptape.tasks import PromptTask
        from griptape.structures import Pipeline
        from griptape.drivers import OpenAiChatPromptDriver

        pipeline = Pipeline(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
            memory=ConversationMemory(),
        )

        pipeline.add_tasks(
            PromptTask(
                "tell me about {{ topic }}", context={"topic": "the lord of the rings"}
            )
        )

        result = pipeline.run()

        assert result.output is not None
        assert re.search("lord", result.output.to_text(), re.IGNORECASE)
