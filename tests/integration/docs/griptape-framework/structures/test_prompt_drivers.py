class TestPromptDrivers:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/structures/prompt-drivers/
    """

    def test_instantiate_prompt_driver(self):
        from griptape.structures import Pipeline
        from griptape.drivers import OpenAiChatPromptDriver

        pipeline = Pipeline(prompt_driver=OpenAiChatPromptDriver(temperature=0.3))

        assert pipeline is not None

    def test_independent_prompt_driver(self):
        from griptape.utils import PromptStack
        from griptape.drivers import OpenAiChatPromptDriver

        stack = PromptStack()

        stack.add_user_input("What's the word, bird?")

        result = OpenAiChatPromptDriver(temperature=1).run(stack)

        assert result.value is not None
