from griptape.drivers import CoherePromptDriver


class TestCoherePromptDriver:
    def test_init(self):
        assert CoherePromptDriver(api_key="foobar")
