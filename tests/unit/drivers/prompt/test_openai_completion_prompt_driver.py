from griptape.drivers import OpenAiCompletionPromptDriver


class TestAzureOpenAiCompletionPromptDriver:
    def test_init(self):
        assert OpenAiCompletionPromptDriver(
            model="davinci"
        )
