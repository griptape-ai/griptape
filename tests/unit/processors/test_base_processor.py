import pytest
from griptape.processors import BasePromptStackProcessor

class TestBasePromptStackProcessor:
    @pytest.fixture
    def processor_instance(self):
        class ConcreteProcessor(BasePromptStackProcessor):
            def before_run(self, prompt):
                return prompt

            def after_run(self, result):
                return result

        return ConcreteProcessor()

    def test_pii_replace_text_default_value(self, processor_instance):
        assert processor_instance.pii_replace_text == "[PII]"

    def test_before_run_abstract_method(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BasePromptStackProcessor().before_run("test_prompt")

    def test_after_run_abstract_method(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BasePromptStackProcessor().after_run("test_result")

    def test_before_run_concrete_implementation(self, processor_instance):
        prompt = "test_prompt"
        result = processor_instance.before_run(prompt)
        assert result == prompt

    def test_after_run_concrete_implementation(self, processor_instance):
        result = "test_result"
        processed_result = processor_instance.after_run(result)
        assert processed_result == result