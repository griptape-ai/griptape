import pytest
from typing import Dict, List, Any
from griptape.processors.prompt_driver_processor import PromptDriverPiiProcessor


class TestPromptDriverPiiProcessor:
    @pytest.fixture
    def processor_instance(self) -> PromptDriverPiiProcessor:
        mask_pii_func = lambda x: "[MASKED]"
        unmask_pii_func = lambda x: "[UNMASKED]"
        return PromptDriverPiiProcessor(None, mask_pii_func, unmask_pii_func)

    def test_before_run(self, processor_instance: PromptDriverPiiProcessor) -> None:
        prompt_stack: Dict[str, List[Dict[str, Any]]] = {"inputs": [{"content": "test_content"}]}
        processed_prompt_stack = processor_instance.before_run(prompt_stack)
        assert processed_prompt_stack["inputs"][0]["content"] == "[MASKED]"

    def test_after_run(self, processor_instance: PromptDriverPiiProcessor) -> None:
        prompt_stack: Dict[str, List[Dict[str, Any]]] = {"inputs": [{"content": "test_content"}]}
        processed_prompt_stack = processor_instance.after_run(prompt_stack)
        assert processed_prompt_stack["inputs"][0]["content"] == "[UNMASKED]"

    def test_mask_pii(self, processor_instance: PromptDriverPiiProcessor) -> None:
        assert processor_instance.mask_pii("test_content") == "[MASKED]"

    def test_unmask_pii(self, processor_instance: PromptDriverPiiProcessor) -> None:
        assert processor_instance.unmask_pii("test_content") == "[UNMASKED]"
