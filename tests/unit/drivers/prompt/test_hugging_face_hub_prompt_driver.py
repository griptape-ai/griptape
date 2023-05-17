from griptape.drivers import HuggingFaceHubPromptDriver


class TestHuggingFaceHubPromptDriver:
    def test_init(self):
        assert HuggingFaceHubPromptDriver(api_token="foobar", repo_id="gpt2")
