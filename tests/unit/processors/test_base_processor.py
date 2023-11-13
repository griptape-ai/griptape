import pytest
from griptape.processors.base_processors import BasePromptStackProcessor, BasePromptDriver

class TestProcessor(BasePromptStackProcessor):
    def before_run(self, prompt):
        return prompt + " before_run"

    def after_run(self, result):
        return result + " after_run"

@pytest.fixture
def driver():
    driver = BasePromptDriver()
    driver.prompt_stack_processors.append(TestProcessor())
    return driver

def test_before_run(driver):
    prompt = "This is a test"
    result = driver.before_run(prompt)
    assert result == "This is a test before_run"

def test_after_run(driver):
    result = "This is a test"
    result = driver.after_run(result)
    assert result == "This is a test after_run"
