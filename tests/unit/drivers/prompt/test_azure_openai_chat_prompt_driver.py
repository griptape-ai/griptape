from griptape.drivers import AzureOpenAiChatPromptDriver


class TestAzureOpenAiChatPromptDriver:
    def test_init(self):
        assert AzureOpenAiChatPromptDriver(
            api_base="foobar",
            deployment_id="foobar",
            model="gpt-4"
        )
