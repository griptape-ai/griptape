import pytest
from unittest.mock import MagicMock, Mock
from griptape.utils import PromptStack
from griptape.processors.amazon_comprehend_processor import AmazonComprehendPiiProcessor

class TestAmazonComprehendPiiProcessor:
    @pytest.fixture
    def processor(self, mocker):
        comprehend_client = MagicMock()
        comprehend_client.detect_pii_entities.return_value = {
            "Entities": [
                {"Text": "Sam Altman", "BeginOffset": 0, "EndOffset": 10},
                {"Text": "email@sam.com", "BeginOffset": 44, "EndOffset": 57}
            ]
        }
        return AmazonComprehendPiiProcessor(comprehend_client=comprehend_client)

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = Mock(spec=PromptStack)
        prompt_stack.inputs = [
            PromptStack.Input(content="Sam Altman is the CEO of OpenAI and his email is email@sam.com, write this statement twice", role=PromptStack.USER_ROLE)
        ]
        return prompt_stack

    def test_before_run(self, processor, prompt_stack):
        result = processor.before_run(prompt_stack)
        assert result.inputs[0].content == "[PII1] is the CEO of OpenAI and his emai[PII0]m.com, write this statement twice"

    @pytest.fixture
    def text_artifact(self, mocker):
        text_artifact = mocker.patch("griptape.processors.amazon_comprehend_processor.TextArtifact")
        text_artifact.value = "[PII0] is the CEO of OpenAI and his email is [PII1], write this statement twice"
        return text_artifact

    def test_after_run(self, processor, text_artifact):
        result = processor.after_run(text_artifact)
        assert result.value == "[PII0] is the CEO of OpenAI and his email is [PII1], write this statement twice"