import pytest

from griptape.drivers import DummyPromptDriver
from griptape.exceptions import DummyError


class TestDummyPromptDriver:
    @pytest.fixture()
    def prompt_driver(self):
        return DummyPromptDriver()

    def test_init(self, prompt_driver):
        assert prompt_driver

    def test_run(self, prompt_driver):
        with pytest.raises(DummyError):
            prompt_driver.run("prompt-stack")

    def test_stream(self, prompt_driver):
        with pytest.raises(DummyError):
            prompt_driver.stream("prompt-stack")
