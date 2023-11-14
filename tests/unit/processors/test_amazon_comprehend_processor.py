import pytest
from unittest.mock import MagicMock
from griptape.processors.base_processors import BasePromptStackProcessor
from griptape.processors.amazon_comprehend_processor import (
    AmazonComprehendPiiProcessor,
)


def custom_filter_func(text: str) -> str:
    return text.replace("John Doe", "[PII]").replace("Jane Doe", "[PII]")


@pytest.fixture
def processor() -> AmazonComprehendPiiProcessor:
    comprehend_client = MagicMock()
    comprehend_client.detect_pii_entities.return_value = {
        "Entities": [{"Text": "John Doe"}, {"Text": "Jane Doe"}]
    }
    return AmazonComprehendPiiProcessor(
        comprehend_client=comprehend_client,
        custom_filter_func=custom_filter_func,
    )


def test_before_run_single_pii(processor: AmazonComprehendPiiProcessor):
    prompt_stack = [{"content": "This is John Doe"}]
    result = processor.before_run(prompt_stack)
    assert result[0]["content"] == "This is [PII]"


def test_before_run_multiple_pii(processor: AmazonComprehendPiiProcessor):
    prompt_stack = [{"content": "This is John Doe. This is Jane Doe"}]
    result = processor.before_run(prompt_stack)
    assert result[0]["content"] == "This is [PII]. This is [PII]"


def test_filter_pii_single(processor: AmazonComprehendPiiProcessor):
    text = "This is John Doe"
    result = processor.filter_pii(text)
    assert result == "This is [PII]"


def test_filter_pii_multiple(processor: AmazonComprehendPiiProcessor):
    text = "This is John Doe. This is Jane Doe"
    result = processor.filter_pii(text)
    assert result == "This is [PII]. This is [PII]"
