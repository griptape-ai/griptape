import contextlib
import os

import pytest

from griptape.drivers import LocalConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestLocalConversationMemoryDriver:
    MEMORY_FILE_PATH = "test_memory.json"

    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        self.__delete_file(self.MEMORY_FILE_PATH)

        yield

        self.__delete_file(self.MEMORY_FILE_PATH)

    def test_store(self):
        prompt_driver = MockPromptDriver()
        memory_driver = LocalConversationMemoryDriver(file_path=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(driver=memory_driver, autoload=False)
        pipeline = Pipeline(prompt_driver=prompt_driver, conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        try:
            with open(self.MEMORY_FILE_PATH):
                raise AssertionError()
        except FileNotFoundError:
            assert True

        pipeline.run()

        with open(self.MEMORY_FILE_PATH):
            assert True

    def test_load(self):
        prompt_driver = MockPromptDriver()
        memory_driver = LocalConversationMemoryDriver(file_path=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(driver=memory_driver, autoload=False, max_runs=5)
        pipeline = Pipeline(prompt_driver=prompt_driver, conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        new_memory = memory_driver.load()

        assert new_memory.type == "ConversationMemory"
        assert len(new_memory.runs) == 2
        assert new_memory.runs[0].input.value == "test"
        assert new_memory.runs[0].output.value == "mock output"
        assert new_memory.max_runs == 5

    def test_autoload(self):
        prompt_driver = MockPromptDriver()
        memory_driver = LocalConversationMemoryDriver(file_path=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(driver=memory_driver)
        pipeline = Pipeline(prompt_driver=prompt_driver, conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        autoloaded_memory = ConversationMemory(driver=memory_driver)

        assert autoloaded_memory.type == "ConversationMemory"
        assert len(autoloaded_memory.runs) == 2
        assert autoloaded_memory.runs[0].input.value == "test"
        assert autoloaded_memory.runs[0].output.value == "mock output"

    def __delete_file(self, file_path) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path)
