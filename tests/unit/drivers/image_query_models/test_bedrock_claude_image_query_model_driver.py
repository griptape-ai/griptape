import pytest
from griptape.drivers import BedrockClaudeImageQueryModelDriver
from griptape.artifacts import ImageArtifact, TextArtifact


class TestBedrockClaudeImageQueryModelDriver:
    def test_init(self):
        assert BedrockClaudeImageQueryModelDriver()

    def test_construct_image_query_request_parameters(self):
        model_driver = BedrockClaudeImageQueryModelDriver()
        params = model_driver.construct_image_query_request_parameters(
            "Prompt String", [ImageArtifact(value=b"test-data", width=100, height=100)]
        )

        assert isinstance(params, dict)
        assert "anthropic_version" in params
        assert params["anthropic_version"] == "bedrock-2023-05-31"
        assert "messages" in params
        assert len(params["messages"]) == 1
        assert "max_tokens" not in params

    def test_construct_image_query_request_parameters_max_tokens(self):
        model_driver = BedrockClaudeImageQueryModelDriver(max_output_tokens=1024)
        params = model_driver.construct_image_query_request_parameters(
            "Prompt String", [ImageArtifact(value=b"test-data", width=100, height=100)]
        )

        assert isinstance(params, dict)
        assert "anthropic_version" in params
        assert params["anthropic_version"] == "bedrock-2023-05-31"
        assert "messages" in params
        assert len(params["messages"]) == 1
        assert "max_tokens" in params
        assert params["max_tokens"] == 1024

    def test_process_output(self):
        model_driver = BedrockClaudeImageQueryModelDriver()
        output = model_driver.process_output({"content": ["ContentBlock"]})

        assert isinstance(output, TextArtifact)
        assert output.value == "['ContentBlock']"

    def test_process_output_bad(self):
        with pytest.raises(KeyError):
            BedrockClaudeImageQueryModelDriver().process_output({"explicitly-not-content": ["ContentBlock"]})
