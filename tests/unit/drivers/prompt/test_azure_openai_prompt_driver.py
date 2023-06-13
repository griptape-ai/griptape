from griptape.drivers import AzureOpenAiPromptDriver


class TestAzureOpenAiPromptDriver:
    def test_init(self):
        assert AzureOpenAiPromptDriver()
