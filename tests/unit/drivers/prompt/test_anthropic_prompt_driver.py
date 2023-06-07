from griptape.drivers import AnthropicPromptDriver


class TestAnthropicPromptDriver:
    def test_init(self):
        assert AnthropicPromptDriver(api_key='1234')
