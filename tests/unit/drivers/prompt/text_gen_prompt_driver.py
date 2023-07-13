from griptape.drivers import TextGenPromptDriver


class TestOpenAiPromptDriver:
    def test_init(self):
        assert TextGenPromptDriver()
