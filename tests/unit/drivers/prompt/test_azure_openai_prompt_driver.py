from griptape.drivers import AzureOpenAiPromptDriver


class TestAzureOpenAiPromptDriver:
    def test_init(self):
        assert AzureOpenAiPromptDriver(
            api_base="foobar",
            deployment_id="foobar",
            model="gpt-4"
        )
