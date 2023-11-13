import pytest
from griptape.processors.base_processors import BasePromptStackProcessor
from griptape.processors.prompt_driver_processor import PromptDriverPiiProcessor

def mask_pii_func(text):
    return text.replace("pii", "xxx")

def unmask_pii_func(text):
    return text.replace("xxx", "pii")

@pytest.fixture
def processor():
    return PromptDriverPiiProcessor(None, mask_pii_func, unmask_pii_func)

def test_before_run(processor):
    prompt_stack = {"inputs": [{"content": "This is a pii"}]}
    result = processor.before_run(prompt_stack)
    assert result["inputs"][0]["content"] == "This is a xxx"

def test_after_run(processor):
    prompt_stack = {"inputs": [{"content": "This is a xxx"}]}
    result = processor.after_run(prompt_stack)
    assert result["inputs"][0]["content"] == "This is a pii"

def test_mask_pii(processor):
    text = "This is a pii"
    result = processor.mask_pii(text)
    assert result == "This is a xxx"

def test_unmask_pii(processor):
    text = "This is a xxx"
    result = processor.unmask_pii(text)
    assert result == "This is a pii"