import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BedrockClaudeImageQueryModelDriver


class TestBedrockClaudeImageQueryModelDriver:
    def test_init(self):
        assert BedrockClaudeImageQueryModelDriver()

    def test_image_query_request_parameters(self):
        model_driver = BedrockClaudeImageQueryModelDriver()
        params = model_driver.image_query_request_parameters(
            "Prompt String", [ImageArtifact(value=b"test-data", width=100, height=100, format="png")], 256
        )

        assert isinstance(params, dict)
        assert "anthropic_version" in params
        assert params["anthropic_version"] == "bedrock-2023-05-31"
        assert "messages" in params
        assert len(params["messages"]) == 1
        assert "max_tokens" in params
        assert params["max_tokens"] == 256

    def test_process_output(self):
        model_driver = BedrockClaudeImageQueryModelDriver()
        output = model_driver.process_output({"content": [{"text": "Content"}]})

        assert isinstance(output, TextArtifact)
        assert output.value == "Content"

    def test_process_output_no_content_key(self):
        with pytest.raises(KeyError):
            BedrockClaudeImageQueryModelDriver().process_output({"explicitly-not-content": ["ContentBlock"]})

    def test_process_output_bad_length(self):
        with pytest.raises(ValueError):
            BedrockClaudeImageQueryModelDriver().process_output({"content": []})

    def test_process_output_no_text_key(self):
        with pytest.raises(KeyError):
            BedrockClaudeImageQueryModelDriver().process_output({"content": [{"not-text": "Content"}]})
