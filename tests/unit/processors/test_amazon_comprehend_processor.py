import pytest
from unittest.mock import MagicMock
from griptape.processors.base_processors import BasePromptStackProcessor
from griptape.processors.amazon_comprehend_processor import AmazonComprehendPiiProcessor

def custom_filter_func(text):
    return text.replace("John Doe", "[PII]")

@pytest.fixture
def processor():
    comprehend_client = MagicMock()
    comprehend_client.detect_pii_entities.return_value = {
        'Entities': [{'Text': 'John Doe'}]
    }
    return AmazonComprehendPiiProcessor(comprehend_client=comprehend_client, custom_filter_func=custom_filter_func)

def test_before_run(processor):
    prompt_stack = [{"content": "This is John Doe"}]
    result = processor.before_run(prompt_stack)
    assert result[0]["content"] == "This is [PII]"

def test_filter_pii(processor):
    text = "This is John Doe"
    result = processor.filter_pii(text)
    assert result == "This is [PII]"
