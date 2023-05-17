from griptape.drivers import OpenAiPromptDriver


class TestOpenAiPromptDriver:
    def test_init(self):
        assert OpenAiPromptDriver()
