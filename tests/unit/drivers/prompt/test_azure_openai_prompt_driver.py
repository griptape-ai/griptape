from griptape.drivers import AzureOpenAiPromptDriver


class TestAzureOpenAiPromptDriver:
    def test_init(self):
        assert AzureOpenAiPromptDriver(
            model="gpt-35-turbo",
            deployment_id="griptape-deployment"
        )
