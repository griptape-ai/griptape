from griptape.drivers import HuggingFacePipelinePromptDriver


class TestHuggingFacePipelinePromptDriver:
    def test_init(self):
        assert HuggingFacePipelinePromptDriver(model="gpt2")
