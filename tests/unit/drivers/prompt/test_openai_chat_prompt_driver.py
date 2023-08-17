from griptape.drivers import OpenAiChatPromptDriver


class TestOpenAiChatPromptDriver:
    def test_init(self):
        assert OpenAiChatPromptDriver(
            model="gpt-4"
        )
