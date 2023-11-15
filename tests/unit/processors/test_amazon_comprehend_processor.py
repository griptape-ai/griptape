import pytest
from unittest.mock import MagicMock
from griptape.processors.base_processors import BasePromptStackProcessor
from griptape.processors.amazon_comprehend_processor import AmazonComprehendPiiProcessor


def custom_filter_func(text: str) -> str:
    return text.replace("John Doe", "[PII]").replace("123 Main St", "[PII]")


@pytest.fixture
def processor() -> AmazonComprehendPiiProcessor:
    comprehend_client = MagicMock()
    comprehend_client.detect_pii_entities.return_value = {"Entities": [{"Text": "John Doe"}, {"Text": "123 Main St"}]}
    return AmazonComprehendPiiProcessor(comprehend_client=comprehend_client, custom_filter_func=custom_filter_func)


def test_before_run_single_pii(processor: AmazonComprehendPiiProcessor) -> None:
    prompt_stack = {"inputs": [{"content": "This is John Doe"}]}
    result = processor.before_run(prompt_stack)
    assert result["inputs"][0]["content"] == "This is [PII]"


def test_before_run_multiple_pii(processor: AmazonComprehendPiiProcessor) -> None:
    prompt_stack = {"inputs": [{"content": "This is John Doe from 123 Main St"}]}
    result = processor.before_run(prompt_stack)
    assert result["inputs"][0]["content"] == "This is [PII] from [PII]"


def test_filter_pii_single(processor: AmazonComprehendPiiProcessor) -> None:
    text = "This is John Doe"
    result = processor.filter_pii(text)
    assert result == "This is [PII]"


def test_filter_pii_multiple(processor: AmazonComprehendPiiProcessor) -> None:
    text = "This is John Doe from 123 Main St"
    result = processor.filter_pii(text)
    assert result == "This is [PII] from [PII]"
