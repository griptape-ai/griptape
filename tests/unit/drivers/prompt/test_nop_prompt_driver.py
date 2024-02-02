from griptape.drivers import NopPromptDriver
import pytest

from griptape.exceptions import NopException


class TestNopPromptDriver:
    @pytest.fixture
    def prompt_driver(self):
        return NopPromptDriver()

    def test_init(self, prompt_driver):
        assert prompt_driver

    def test_try_run(self, prompt_driver):
        with pytest.raises(NopException):
            prompt_driver.try_run("prompt-stack")

    def test_try_stream_run(self, prompt_driver):
        with pytest.raises(NopException):
            prompt_driver.try_run("prompt-stack")
