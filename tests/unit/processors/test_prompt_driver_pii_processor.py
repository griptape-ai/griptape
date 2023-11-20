import pytest
from griptape.processors import PromptDriverPiiProcessor
from griptape.utils import PromptStack
from griptape.artifacts import TextArtifact

class TestPromptDriverPiiProcessor:
    @pytest.fixture
    def processor_instance(self):
        mask_pii_func = lambda x: ("[MASKED]", {})
        unmask_pii_func = lambda x, y=None: "[UNMASKED]"
        return PromptDriverPiiProcessor(None, mask_pii_func, unmask_pii_func)

    def test_before_run(self, processor_instance):
        prompt_stack = PromptStack(inputs=[PromptStack.Input(content="test_content", role=PromptStack.USER_ROLE)])
        processed_prompt_stack = processor_instance.before_run(prompt_stack)
        assert processed_prompt_stack.inputs[0].content == "[MASKED]"

    def test_after_run(self, processor_instance):
        text_artifact = TextArtifact(value="test_content")
        processed_text_artifact = processor_instance.after_run(text_artifact)
        assert processed_text_artifact.value == "[UNMASKED]"

    def test_mask_pii(self, processor_instance):
        assert processor_instance.mask_pii("test_content") == ("[MASKED]", {})

    def test_unmask_pii(self, processor_instance):
        assert processor_instance.unmask_pii("test_content") == "[UNMASKED]"