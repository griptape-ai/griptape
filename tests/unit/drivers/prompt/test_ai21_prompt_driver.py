from griptape.drivers import Ai21PromptDriver


class TestAi21PromptDriver:
    def test_init(self):
        assert Ai21PromptDriver(api_key="foo")
