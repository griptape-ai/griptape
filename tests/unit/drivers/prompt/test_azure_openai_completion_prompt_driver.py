from griptape.drivers import AzureOpenAiCompletionPromptDriver


class TestAzureOpenAiCompletionPromptDriver:
    def test_init(self):
        assert AzureOpenAiCompletionPromptDriver(
            api_base="foobar",
            deployment_id="foobar",
            model="davinci"
        )
