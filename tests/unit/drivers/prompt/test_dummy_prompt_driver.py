from griptape.drivers import DummyPromptDriver
import pytest

from griptape.exceptions import DummyException


class TestDummyPromptDriver:
    @pytest.fixture
    def prompt_driver(self):
        return DummyPromptDriver()

    def test_init(self, prompt_driver):
        assert prompt_driver

    def test_try_run(self, prompt_driver):
        with pytest.raises(DummyException):
            prompt_driver.try_run("prompt-stack")

    def test_try_stream_run(self, prompt_driver):
        with pytest.raises(DummyException):
            prompt_driver.try_run("prompt-stack")
